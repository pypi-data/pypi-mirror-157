from servicefoundry.internal.predictor import Predictor
from servicefoundry.requirements.python_requirements import PythonRequirements


def requirements_file_interceptor(predictor: Predictor):
    def _requirements_file_interceptor(source_lines):
        requirements = PythonRequirements(source_lines)
        requirements.update_requirements_txt(predictor.get_dependencies())
        return requirements.get_requirements_txt()

    return _requirements_file_interceptor
