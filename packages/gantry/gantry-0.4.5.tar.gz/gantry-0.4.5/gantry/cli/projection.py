import json
import logging
import os
import platform
import pprint
import re
import subprocess
import tempfile
from typing import List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

import click
import yaml

import gantry
from gantry.api_client import APIClient
from gantry.const import PROD_API_URL
from gantry.utils import generate_gantry_name

logger = logging.getLogger(__name__)

_HANDLER_FILENAME = "_gantry_handler"
_REQUIRED_DEPS = ["pandas"]
_VALID_PYVERS = ("3.6", "3.7", "3.8", "3.9")


@click.group()
def projection():
    """
    Use this to register a new custom projection to Gantry.
    """


@projection.command()
@click.option("--filename", type=click.Path())
@click.option("--logs_location", default=PROD_API_URL, type=click.STRING)
@click.option("--api_url", default=PROD_API_URL, type=click.STRING)
@click.option("--api_key", type=click.STRING)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Enable dry run to test resulting Docker image before uploading to Gantry",
)
def register(filename, logs_location, api_url, api_key=None, dry_run=False):
    init_kwargs = {}
    if logs_location:
        init_kwargs["logs_location"] = logs_location
    if filename:
        init_kwargs["filename"] = filename
    if api_url:
        init_kwargs["api_url"] = api_url
    if api_key:
        init_kwargs["api_key"] = api_key
    gantry.init(**init_kwargs)
    if not api_url:
        click.secho("No api_url specified", fg="cyan")
    else:
        parsed_url = urlparse(api_url)
        if not parsed_url.scheme.startswith("http"):
            click.secho("API url must start with http or https", fg="cyan")
            return
        api_url = urlunparse(parsed_url)

    api_client = APIClient(origin=api_url, api_key=api_key)
    print(f"Registering custom projection to url {api_url} using logs location at {logs_location}")
    if not filename.endswith(".yaml"):
        raise click.ClickException(
            "The supplied file to gantry projection register must be a .yaml file that "
            "contains a projection definition."
        )
    with open(filename, "r") as stream:
        metric_def_dict = yaml.safe_load(stream)

    for _, metric_def in metric_def_dict.items():
        if not _register_function(api_client, metric_def, dry_run):
            return False


def _register_function(api_client: APIClient, metric_def: dict, dry_run: bool) -> bool:
    click.secho("Registering a custom projection with definition:", fg="cyan")
    click.secho(pprint.pformat(metric_def))

    click.secho("Creating projection function bundle...", fg="cyan")
    metric_or_proj_name, def_type = _get_name_and_type(metric_def)
    runtime_lang = "python"  # we only support python right now
    runtime_version = _get_runtime_version(metric_def.get("python_version"))
    # TODO: support building docker images here
    # if the zip file is too large, our upload request may fail
    image_name = _package_function(
        metric_or_proj_name,
        def_type,
        metric_def["entrypoint"],
        metric_def["function_name"],
        metric_def.get("requirements", []),
        runtime_version,
    )

    metric_def["runtime"] = {"lang": runtime_lang, "version": runtime_version}
    metric_def["handler"] = {"file_name": _HANDLER_FILENAME, "func_name": "handler"}

    if dry_run:
        click.secho("Dry run complete", fg="cyan")
        return True

    # see where we should upload the zip file based on Gantry's configuration
    resp_content = api_client.request(
        "GET",
        "/api/v1/metrics/pre-upload",
        params={"name": metric_or_proj_name},
    )

    # check that our runtime is supported
    if runtime_version not in resp_content["accepted_runtimes"].get(runtime_lang, []):
        click.secho(
            "Registering projection failed. "
            "Runtime {} {} is not supported. Accepted runtimes are:".format(
                runtime_lang, runtime_version
            ),
            fg="red",
        )
        click.secho(pprint.pformat(resp_content["accepted_runtimes"]))
        return False

    with tempfile.TemporaryDirectory() as tmpdirname:
        if resp_content.get("upload_url"):
            uploading_message = "Uploading function bundle... "
            click.secho(uploading_message, nl=False)

            _upload_package(image_name, resp_content["upload_url"])

            metric_def["s3_key"] = resp_content["s3_key"]
            files = None
        else:
            package_zip = _save_package(image_name, tmpdirname)
            files = {"file": open(package_zip, "rb")}

        waiting_message = "Sending request... "
        click.secho(waiting_message, nl=False)
        resp_content = api_client.request(
            "POST",
            "/api/v1/metrics",
            data={"metric": json.dumps(metric_def)},
            files=files,
        )

    click.echo("\b" * len(waiting_message), nl=False)

    if resp_content["response"] == "error":
        click.secho("Registering projection failed.\n >>>> Error message: ", fg="red", nl=False)
        click.secho(resp_content["error"])
    else:
        click.secho("Registering projection succeeded!", fg="green")

    return True


def _get_name_and_type(metric_def: dict) -> Tuple[str, str]:
    if "metric_name" in metric_def:
        raise ValueError(
            "We currently do not support custom metrics, please name the field 'metric_name' "
            "to 'projection_name'"
        )
        # return metric_def["metric_name"], "metric"
    elif "projection_name" in metric_def:
        return metric_def["projection_name"], "projection"
    raise ValueError(
        "There was an error: 'projection_name' must be specified in the configuration yaml!"
    )


_METRIC_HANDLER_TMPL = """
import pandas as pd

# in case module_path has dashes
from importlib import import_module
module = import_module("{module_path}")
func = module.{function_name}

def handler(event, context):
    args = [pd.Series(arg) for arg in event['args']]
    return func(*args)
"""

_PROJECTION_HANDLER_TMPL = """
# in case module_path has dashes
from importlib import import_module
module = import_module("{module_path}")
func = module.{function_name}

def handler(event, context):
    args = event['args']
    return func(*args)
"""

_DOCKERFILE_TMPL = """
FROM public.ecr.aws/lambda/python:{runtime_version}

RUN yum update -y && \
  yum install -y make glibc-devel gcc-c++ patch zip curl && \
  rm -Rf /var/cache/yum

RUN pip install --target "${{LAMBDA_TASK_ROOT}}" {requirements}

COPY . "${{LAMBDA_TASK_ROOT}}"

WORKDIR "${{LAMBDA_TASK_ROOT}}"

CMD [ "{handler}" ]
"""


def _generate_handler(entrypoint: str, function_name: str, def_type: str):
    module_path = entrypoint.replace("/", ".")
    module_path = re.sub(r"\.py$", "", module_path)

    # TODO: aws lambda has a 6MB payload limit. support getting data from s3
    handler_type_to_handler_tmpl = {
        "projection": _PROJECTION_HANDLER_TMPL,
        "metric": _METRIC_HANDLER_TMPL,
    }

    handler = handler_type_to_handler_tmpl[def_type].format(
        module_path=module_path, function_name=function_name
    )

    return handler


def _package_function(
    name: str,
    def_type: str,
    entrypoint: str,
    function_name: str,
    deps: List[str],
    runtime_version: str,
) -> str:
    packages = []
    for dep in deps:
        packages.append(f"'{dep}'")
    packages += _REQUIRED_DEPS

    handler_content = _generate_handler(entrypoint, function_name, def_type)
    handler_filename = "{}.py".format(_HANDLER_FILENAME)
    with open(handler_filename, "w") as f:
        f.write(handler_content)
    handler = "{}.handler".format(_HANDLER_FILENAME)
    try:
        dockerfile = _DOCKERFILE_TMPL.format(
            runtime_version=runtime_version, requirements=" ".join(packages), handler=handler
        )
        tag = generate_gantry_name(name)

        # build via subprocess so we get nice familiar docker output
        proc = subprocess.run(
            ["docker", "buildx", "build", "--platform", "linux/amd64", "-t", tag, "-f", "-", "."],
            input=dockerfile.encode("utf-8"),
        )
        if proc.returncode != 0:
            raise Exception("Failed to build Docker image for custom projection function")
    finally:
        os.remove(handler_filename)

    click.secho("Function packaged as {}".format(tag), fg="cyan")

    return tag


def _upload_package(image_name: str, presigned_url: str) -> None:
    proc = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "bash",
            image_name,
            "-c",
            f"zip -qr function.zip . && curl --upload-file function.zip '{presigned_url}'",
        ]
    )
    if proc.returncode != 0:
        raise Exception("Failed to upload function package for custom projection function")


def _save_package(image_name: str, dirname: str) -> str:
    output_filename = os.path.join(dirname, "function.zip")
    proc = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{dirname}:/mnt",
            "--entrypoint",
            "zip",
            image_name,
            "-r",
            "/mnt/function.zip",
            ".",
        ]
    )
    if proc.returncode != 0:
        raise Exception("Failed to create function package for custom projection function")

    return output_filename


def _get_runtime_version(version: Optional[str] = None) -> str:
    if not version:
        version_tuple = platform.python_version_tuple()
        version = "{}.{}".format(version_tuple[0], version_tuple[1])

        if version not in _VALID_PYVERS:
            version = _VALID_PYVERS[-1]
            click.secho("Defaulting to Python version {}".format(version), fg="yellow")

    return version


class DependenciesInstallError(Exception):
    pass
