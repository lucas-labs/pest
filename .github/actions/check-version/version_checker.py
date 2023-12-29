import os
import sys

import tomli
from packaging import version

# def get_public_version(project_name: str, is_test = False) -> Version:
#     response = requests.get(
#         f'https://{"test." if is_test else ""}pypi.org/pypi/{project_name}/json'
#     )
#     response.raise_for_status()
#     return version.parse(json.loads(response.content)['info']['version'])


if __name__ == '__main__':
    pyproject_toml_path = sys.argv[1]

    with open(pyproject_toml_path, 'rb') as f:
        project = tomli.load(f)

    print(project)

    # project_version = version.parse(project['tool']['poetry']['version'])
    name = project.get('tool', {}).get('poetry', {}).get('name', None)
    project_version = version.parse(project.get('tool', {}).get('poetry', {}).get('version', None))
    description = project.get('tool', {}).get('poetry', {}).get('description', None)
    is_test = False
    # public_project_version = get_public_version(project['project']['name'], is_test)

    with open(os.environ['GITHUB_OUTPUT'], 'at') as f:
        # f.write(
        #     f'local_version_is_higher={str(project_version > public_project_version).lower()}\n'
        # )
        # f.write(f'public_version={str(public_project_version)}\n')
        f.write(f'local-version={str(project_version)}\n')
        f.write(f'package-name={name}\n')
        f.write(f'package-description={description}\n')
