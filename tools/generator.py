
import ast
import os
import pathlib
import subprocess
import sys
from inspect import getsource

from pest.metadata.types.controller_meta import ControllerMeta
from pest.metadata.types.handler_meta import HandlerMeta
from pest.metadata.types.module_meta import ModuleMeta
from pest.utils.colorize import c

metas = [
    ModuleMeta,
    HandlerMeta,
    ControllerMeta
]

types_path = os.path.join(os.getcwd(), 'pest', 'decorators', 'dicts')


def to_snake_case(name: str) -> str:
    return ''.join([
        '_' + char.lower() if char.isupper() else char
        for char in name
    ]).lstrip('_')


def extract_imports(code: str) -> list[tuple[str, list[str]]]:
    tree = ast.parse(code)
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, None))
        elif isinstance(node, ast.ImportFrom):
            module = '.' * node.level + (node.module or '')
            comma_sep_names = [alias.name for alias in node.names]

            imports.append((module, comma_sep_names))

    return imports


def fix_rel_import(import_line: str, module_path: str, destination: str) -> str:
    if not import_line.startswith('.'):
        return import_line

    module_dir = pathlib.Path(module_path).parent
    new_path = pathlib.Path(destination)

    def import_path_to_os_relative_path(import_path: str) -> str:
        parts = import_path.lstrip('.').split('.')
        parent_dirs = ['..'] * (len(import_path) - len(import_path.lstrip('.')) - 1)
        return f"./{'/'.join(parent_dirs + parts)}.py"

    relative_import_path = import_path_to_os_relative_path(import_line)
    absolute_import_path = os.path.abspath(
        os.path.join(module_dir, relative_import_path)
    )

    relative_path = pathlib.Path(os.path.relpath(absolute_import_path, new_path))
    relative_parts = list(
        map(lambda part: '' if part == '..' else (
            str(part).replace('.py', '')
        ), relative_path.parts)
    )

    return f"{'.'.join(relative_parts)}"


def extract_class_vars(code: str, class_name: str) -> list[tuple[str, str]]:
    class ClassVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.variables = []

        def _should_expose(self, item: ast.AnnAssign | ast.Assign) -> bool:
            value = item.value
            if (isinstance(value, ast.Call)):
                if isinstance(value.func, ast.Name) and value.func.id == 'field':
                    keywords = value.keywords
                elif (
                    isinstance(value.func, ast.Attribute) and
                    value.func.attr == 'field' and
                    isinstance(value.func.value, ast.Name) and
                    value.func.value.id == 'dataclasses'
                ):
                    keywords = value.keywords
                else:
                    keywords = []

                for keyword in keywords if keywords is not None else []:
                    meta = None
                    if (keyword.arg == 'metadata' and isinstance(keyword.value, ast.Dict)):
                        meta = dict(zip(keyword.value.keys, keyword.value.values))

                    for k, v in meta.items() if meta is not None else []:
                        if (
                            isinstance(k, ast.Constant) and
                            isinstance(v, ast.Constant) and
                            k.value == 'expose' and
                            v.value is False
                        ):
                            return False

            return True

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            if node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.Assign, ast.AnnAssign)):
                        targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                        for target in targets:
                            if isinstance(target, ast.Name):
                                if not self._should_expose(item):
                                    continue

                                var_name = target.id
                                var_type = ast.get_source_segment(
                                    code, item.value
                                    if isinstance(item, ast.Assign) else item.annotation
                                )
                                self.variables.append((var_name, var_type))

    visitor = ClassVisitor()
    visitor.visit(ast.parse(code))

    return visitor.variables


def extract_type_aliases(code: str) -> list[str]:
    type_aliases = []

    def visit_node(node: ast.AST) -> None:
        if isinstance(node, ast.AnnAssign):
            target, annotation = node.target, node.annotation
            if (
                isinstance(target, ast.Name) and
                isinstance(annotation, ast.Name) and
                annotation.id == 'TypeAlias'
            ):
                type_aliases.append(target.id)

    tree = ast.parse(code)
    for node in ast.walk(tree):
        visit_node(node)

    return type_aliases


def relcwd(path: str) -> str:
    return os.path.relpath(path, os.getcwd()).replace('\\', '/')


def write_file(
    typed_dict_path: str,
    module_path: str,
    module_src: str,
    meta_name: str,
    new_name: str | None = None
) -> None:
    relative_module_path_from_cwd = (
        relcwd(module_path)
        .replace('\\', '/')
    )

    with open(typed_dict_path, 'w') as f:
        # docstring at the top of the file indicating that it is auto-generated by the tool
        f.writelines([
            '"""\n',
            f'Module providing typed dicts for the metadata {meta_name}:\n',
            f'- {relative_module_path_from_cwd}\n\n',
            'ATTENTION:\n',
            'This file was auto-generated by tools/generator.py.\n',
            'Do not edit manually.\n',
            '"""\n\n'
        ])

        f.write('from typing import TypedDict\n')
        # imports
        for module, names in extract_imports(module_src):
            if names is None:
                f.write(f'import {module}\n')
            else:
                module = fix_rel_import(module, module_path, typed_dict_path)
                f.write(f'from {module} import {", ".join(names)}\n')

            # import type aliases
        for alias in extract_type_aliases(module_src):
            # type aliases are defined in the same module as the class, so get the file name
            # of the module (without the .py extension) and import the alias from there
            module_name = fix_rel_import(
                f'.{pathlib.Path(module_path).stem}',
                module_path,
                typed_dict_path
            )
            f.write(f'from {module_name} import {alias}\n')

            # class as TypedDict
        f.write(f'class {new_name or meta_name}(TypedDict, total=False):\n')
        for var_name, var_type in extract_class_vars(module_src, meta_name):
            f.write(f'    {var_name}: {var_type}\n')  # noqa: S603


def types() -> None:
    print(
        f'🐀 ⇝  Generating {c("`TypeDict`", attrs=["bold"])} '
        f'for {c("`Metas`", attrs=["bold"])} in {c(relcwd(types_path), color="blue")}\n'
    )

    # create the types directory if it doesn't exist
    pathlib.Path(types_path).mkdir(parents=True, exist_ok=True)

    for meta in metas:
        meta_name = str(meta.__name__)
        type_dict_class_name = f'{meta_name}Dict'

        print(
            f'📑 Generating {c(type_dict_class_name, color="light_magenta")} '
            f'from {c(meta_name, color="blue")} in {c(relcwd(types_path), color="blue")}'
        )

        typed_dict_path = os.path.join(
            types_path,
            f'{to_snake_case(meta.__name__)}.py'
        ).replace('_meta', '_dict')

        module = sys.modules[meta.__module__]
        module_path = str(module.__file__)
        module_src = getsource(module)

        write_file(typed_dict_path, module_path, module_src, meta_name, type_dict_class_name)
        print('    ⚬ The module was generated')

        # lint the new file using ruff
        command = f'poetry run ruff {typed_dict_path} --fix'

        print('    ⚬ Linting')
        print(
            f'    ⚬ {c("$", color="yellow")} {c("poetry", color="yellow", attrs=["bold"])} '
            f'run ruff '
            f'{c("--fix", attrs=["dark"])}\n'


        )
        subprocess.run(command, check=True, capture_output=True)  # noqa: S603

    print(
        f'\n🐀 ⇝  {c("`TypeDict`", attrs=["bold"])} '
        f'generation {c("completed", color="green")}\n'
    )


if __name__ == '__main__':
    types()
