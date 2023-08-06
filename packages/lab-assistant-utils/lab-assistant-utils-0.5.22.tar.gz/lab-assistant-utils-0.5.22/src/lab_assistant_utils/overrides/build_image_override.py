from lab_assistant_utils.docker import lab_build_image_impl


project_name = ''
project_version = ''
project_path = ''


def lab_build_image(registry_name: str):
    lab_build_image_impl(registry_name, project_name, project_version, project_path)
