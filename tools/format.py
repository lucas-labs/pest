import os
import subprocess

import black
from ruff.__main__ import find_ruff_bin

from pest.utils.colorize import c

ERR = 1
OKI = 0


def check() -> int:
    """runs black on check mode and returns 0 if no changes would be made, 1 otherwise"""
    args = ['--check', '.']
    print(f'\n{c("$ ", color="green")}{c("black", color="blue")} {" ".join(args)}\n')

    try:
        black.main(args)
    except SystemExit:
        return ERR
    else:
        return OKI


def fix() -> int:
    """runs black on fix mode and returns 0 if no changes were made, 1 otherwise"""
    args = ['.']
    print(f'\n{c("$ ", color="green")}{c("black", color="blue")} {" ".join(args)}\n')

    try:
        black.main()
    except SystemExit:
        return ERR
    else:
        return OKI


def lint_check() -> int:
    """runs ruff on check mode and returns 0 if no changes would be made, 1 otherwise"""
    ruff = find_ruff_bin()
    args = ['check', '.']

    print(f'\n{c("$ ", color="green")}{c(ruff, color="blue")} {" ".join(args)}\n')

    completed_process = subprocess.run([os.fsdecode(ruff), *args])  # noqa: S603
    if completed_process.returncode != 0:
        return ERR

    return OKI


def lint_fix() -> int:
    """runs ruff on fix mode and returns 0 if no changes were made, 1 otherwise"""
    ruff = find_ruff_bin()
    args = ['check', '.', '--fix']

    print(f'\n{c("$ ", color="green")}{c(ruff, color="blue")} {" ".join(args)}\n')

    completed_process = subprocess.run([os.fsdecode(ruff), *args])  # noqa: S603
    if completed_process.returncode != 0:
        return ERR

    return OKI
