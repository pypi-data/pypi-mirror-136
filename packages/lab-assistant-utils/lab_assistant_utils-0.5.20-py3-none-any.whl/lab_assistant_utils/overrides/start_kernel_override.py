from lab_assistant_utils.kernel_cli import lab_start_kernel_impl
from lab_assistant_utils.docker import DockerRunOptions

project_name = ''
project_version = ''
project_path = ''


def lab_start_kernel(connection, registry_name: str, options: DockerRunOptions):
    kernel_image = f"{registry_name}/{project_name}:{project_version}"
    lab_start_kernel_impl(connection, kernel_image, project_name, project_path, options)
