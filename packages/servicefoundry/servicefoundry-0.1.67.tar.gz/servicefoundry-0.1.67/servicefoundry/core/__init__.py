from servicefoundry.core.component import Gradio, Parameters, Service, Webapp
from servicefoundry.core.login import login
from servicefoundry.core.logout import logout
from servicefoundry.core.notebook.notebook_util import is_notebook
from servicefoundry.core.requirements import gather_requirements
from servicefoundry.service_definition.definition import CPU, Memory

if is_notebook():
    try:
        import ipywidgets
    except ImportError:
        print("Run `pip install ipywidgets` to use notebook features.")
