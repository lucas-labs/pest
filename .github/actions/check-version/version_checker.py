import os
import sys

import tomli
from packaging import version

if __name__ == '__main__':
    pyproject_toml_path = sys.argv[1]

    with open(pyproject_toml_path, 'rb') as f:
        project = tomli.load(f)

    name = project.get('project', {}).get('name', None)
    project_version = version.parse(project.get('project', {}).get('version', None))
    description = project.get('project', {}).get('description', None)

    print(f'local-version: {name}')
    print(f'package-name: {project_version}')
    print(f'package-description: {description}')

    with open(os.environ['GITHUB_OUTPUT'], 'at') as f:
        f.write(f'local-version={str(project_version)}\n')
        f.write(f'package-name={name}\n')
        f.write(f'package-description={description}\n')
