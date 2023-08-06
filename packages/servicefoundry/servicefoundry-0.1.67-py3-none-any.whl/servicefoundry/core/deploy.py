from servicefoundry.core.notebook.notebook_util import get_default_callback, is_notebook
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.sfy_deploy.deploy import deploy as sfy_deploy

process = None


# def _deploy_local(packaged_output, callback):
#     global process
#     if not is_notebook():
#         process = __deploy_local(packaged_output, callback)
#         process.join()
#     else:
#         callback.start_panel()
#         if process is not None and process.is_alive():
#             callback.print_line("Stopping the old process.")
#             process.stop()
#             process.join()
#             callback.print_line("Old process stopped.")
#         process = __deploy_local(packaged_output, callback)
#         callback.close_panel()
#
#
# def deploy_local():
#     callback = get_default_callback()
#     packaged_output = package(callback=callback)
#     return _deploy_local(packaged_output, callback)


def deploy(directory="./"):
    callback = get_default_callback()
    client = ServiceFoundryServiceClient.get_client()
    deployment = sfy_deploy(directory, client)
    client.tail_logs(deployment["runId"], wait=True, callback=callback)
