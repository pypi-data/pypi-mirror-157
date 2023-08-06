import logging
from pathlib import Path

import rich_click as click

import servicefoundry.core as sfy
from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.const import COMMAND_CLS, GROUP_CLS
from servicefoundry.cli.io.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.sfy_deploy.deploy import deploy

logger = logging.getLogger(__name__)

LOCAL = "local"
REMOTE = "remote"


@click.group(
    name="deploy",
    cls=GROUP_CLS,
    invoke_without_command=True,
    help="Deploy servicefoundry Service",
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(exists=False, file_okay=False, writable=True, resolve_path=True),
    default="./",
    help="directory to init in",
)
@click.pass_context
@handle_exception_wrapper
def deploy_command(ctx, directory):
    if ctx.invoked_subcommand is None:
        tf_client = ServiceFoundryServiceClient.get_client()
        callback = RichOutputCallBack()
        deployment = deploy(Path(directory), tf_client)
        if not CliConfig.get("json"):
            tf_client.tail_logs(deployment["runId"], callback=callback, wait=True)


@click.command(name="function", cls=COMMAND_CLS, help="Deploy a python function.")
@click.option("--python_service_file", type=click.STRING, default=None)
@click.option("--service_name", type=click.STRING, default=None)
@click.option("--workspace", type=click.STRING, default=None)
@click.option("--python_version", type=click.STRING, default=None)
@click.option("--local", is_flag=True, default=False)
@handle_exception_wrapper
def function_command(
    python_service_file, service_name, workspace, python_version, local
):
    _component_command(
        sfy.Service, python_service_file, service_name, workspace, python_version, local
    )


@click.command(name="webapp", cls=COMMAND_CLS, help="Deploy a python function.")
@click.option("--python_service_file", type=click.STRING, default=None)
@click.option("--service_name", type=click.STRING, default=None)
@click.option("--workspace", type=click.STRING, default=None)
@click.option("--python_version", type=click.STRING, default=None)
@click.option("--local", is_flag=True, default=False)
@handle_exception_wrapper
def webapp_command(python_service_file, service_name, workspace, python_version, local):
    _component_command(
        sfy.Webapp, python_service_file, service_name, workspace, python_version, local
    )


def _component_command(
    cls, python_service_file, service_name, workspace, python_version, local
):
    raise RuntimeError("TBD")


def get_deploy_command():
    deploy_command.add_command(function_command)
    deploy_command.add_command(webapp_command)
    return deploy_command
