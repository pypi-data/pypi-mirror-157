from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.parameters import OptionsParameter, Parameter, WorkspaceParameter
from servicefoundry.lib.exceptions import ConfigurationException


class DefaultInputHook(InputHook):
    def _get_default_param(self, param: Parameter, options=None):
        default = param.default if param.default else param.suggest
        default = (
            f" Suggested value is {default}."
            if default is not None and default.strip() != ""
            else ""
        )
        options = f" Valid choices are {options}. " if options else ""

        raise ConfigurationException(
            f"Parameter {param.id} is not provided." + default + options
        )

    def confirm(self, param: Parameter, default=False):
        return False

    def ask_string(self, param: Parameter):
        return self._get_default_param(param)

    def ask_number(self, param: Parameter):
        return self._get_default_param(param)

    def ask_file_path(self, param: Parameter):
        return self._get_default_param(param)

    def ask_python_file(self, param: Parameter):
        return self._get_default_param(param)

    def ask_option(self, param: OptionsParameter):
        value = self._get_default_param(param, options=param.options)
        if value in param.options:
            return value
        raise ConfigurationException(
            f"For parameter {param.id} provided value {value} "
            f"is not in [{','.join(param.options.keys())}]"
        )

    def ask_workspace(self, param: WorkspaceParameter):
        workspace_choices = self.get_workspace_choices()
        workspaces = [workspace_choice[1] for workspace_choice in workspace_choices]
        value = self._get_default_param(param, options=workspaces)
        if value in workspaces:
            return value
        raise ConfigurationException(
            f"For parameter {param.id} provided value {value} "
            f"is not in [{' ,'.join(param.options.keys())}]"
        )
