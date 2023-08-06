from servicefoundry import lib
from servicefoundry.core.notebook.notebook_util import get_default_callback


def logout():
    lib.logout(output_hook=get_default_callback())
