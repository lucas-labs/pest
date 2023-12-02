"""
### 🐀 ⇝ patch tool
This tool is used to patch files in the venv so that we don't need to wait for a new release of
a library to fix a bug or add a feature while we're developing.

It lets us keep our changes in a separate directory that can be commited to github, keeping the
modifications and the original files in the repository, so that we can easily reapply them when
we update the library or roll back to the original version.

#### Sure, but how it works?

First, create a patch configuration file in the patch directory. This file should be a JSON file
like this:

```json
{
    "patches": [
        {
            "original": "rodi/__init__.py",
            "replace": "rodi/__init__.py"
        }
    ]
}
```

This file should be named `patches.json` and should be in the `.patches` directory in the root
of the project. Each file in the `patches` list should have an `original` and a `replace` key.

Then:
1. Create your replacement file in the patch directory. In the example above, the replacement
    file would be `./.patches/rodi/__init__.py`.
2. Make your changes to the replacement file.
3. Run `make_patches` function to create the patch files. This will create a backup of the
    original file in `./.patches/rodi/__init__.py.original` and a patch file in
    `./.patches/rodi/__init__.py.original.patch`.
4. Make sure the .patch file looks reasonable.
5. Run `apply_patches` function to apply the patches. This will apply the .patch file to the
    original file.

Done! You can now use your patched library.
"""


import os
import shutil
from subprocess import run

from pydantic import BaseModel

from pest.utils.colorize import c


def get_venv_path() -> str:
    command = ['poetry', 'env', 'info', '-p']
    return run(command, capture_output=True).stdout.decode('utf-8').strip()  # noqa: S603


def get_patches_paths() -> tuple[str, str]:
    possible_paths = ['.patch', '.patches', 'patches', 'patch']
    for path in possible_paths:
        patch_dir = os.path.join(os.getcwd(), path)

        if os.path.isdir(patch_dir):
            patchcfg = os.path.join(patch_dir, 'patches.json')
            if os.path.isfile(patchcfg):
                return (patch_dir, patchcfg)

    # none exists, create .patches
    patch_dir = os.path.join(os.getcwd(), '.patches')
    os.mkdir(patch_dir)
    patchcfg = os.path.join(patch_dir, 'patches.json')
    with open(patchcfg, 'w') as f:
        f.write('{"patches": []}')
    return (patch_dir, patchcfg)


class Patch(BaseModel):
    original: str
    replace: str


class Cfg(BaseModel):
    patches: list[Patch]


venv_path = get_venv_path()
patch_dir, cfg_path = get_patches_paths()
cfg = Cfg.parse_file(cfg_path)
ERR = 1
OK = 0


def init(src: str, dst: str) -> None:
    shutil.copyfile(src, dst)


def get_paths(patch: Patch) -> dict:
    original_path = os.path.join(venv_path, 'Lib/site-packages', patch.original)
    replace_path = os.path.join(patch_dir, patch.replace)

    # check both files exist
    if not os.path.isfile(original_path):
        raise FileNotFoundError(f'Original file {original_path} not found')
    if not os.path.isfile(replace_path):
        raise FileNotFoundError(f'Replace file {replace_path} not found')

    # get dir of replace_path:
    replace_dir = os.path.dirname(replace_path)
    original_file_name = os.path.basename(original_path)
    original_copy_path = os.path.join(replace_dir, original_file_name + '.original')
    patch_file_path = original_copy_path + '.patch'

    return {
        'original_path': original_path,
        'replace_path': replace_path,
        'replace_dir': replace_dir,
        'original_file_name': original_file_name,
        'original_copy_path': original_copy_path,
        'patch_file_path': patch_file_path,
    }


def make_patches() -> int:
    # for each patch in cfg.patches, we copy the original with name {name}.original
    # and replace the original with the replace in venv_path/{original}
    patch_files_created = []

    for patch in cfg.patches:
        paths = get_paths(patch)

        # backup original
        print(
            c(f'Copying {paths["original_path"]} to {paths["original_copy_path"]}', color='green')
        )
        shutil.copyfile(paths['original_path'], paths['original_copy_path'])

        # make diff
        command = ['diff', '-u', paths['original_copy_path'], paths['replace_path']]
        print(f'Running {c(" ".join(command), color="blue")}')
        result = run(command, capture_output=True, encoding='utf-8')  # noqa: S603

        # make patch file
        patch_file_path = paths['original_copy_path'] + '.patch'
        print(c(f'Creating patch file {patch_file_path}', color='green'))
        with open(patch_file_path, 'w') as f:
            f.write(result.stdout.strip())

        patch_files_created.append(patch_file_path)

    print(c('Patches created:', color='green'))
    for patch_file_path in patch_files_created:
        print(c(patch_file_path, color='blue'))

    print(f'\nRun {c("poetry run patch:apply", color="blue")} to apply patches')

    return OK


def apply_patches() -> int:
    # patch {original} -i {original_file_name}.patch
    for patch in cfg.patches:
        paths = get_paths(patch)

        if not os.path.isfile(paths['patch_file_path']):
            print(c(f'Patch file {paths["patch_file_path"]} not found', color='red'))
            return ERR

        command = ['patch', paths['original_path'], '-i', paths['patch_file_path']]
        print(f'Running {c(" ".join(command), color="blue")}')
        result = run(command, capture_output=True, encoding='utf-8')  # noqa: S603
        print(result.stdout.strip())

    return OK
