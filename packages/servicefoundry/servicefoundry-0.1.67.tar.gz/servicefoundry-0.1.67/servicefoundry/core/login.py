from servicefoundry import lib
from servicefoundry.core.notebook.notebook_util import get_default_callback


def login(api_key=None):
    lib.login(
        api_key=api_key,
        interactive=False if api_key else True,
        output_hook=get_default_callback(),
    )
