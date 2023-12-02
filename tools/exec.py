"""
### 🐀 ⇝ `exec.py` - Execute a tool

This module provides functionality to execute a specific tool from the './tasks' directory.

The tool to be executed is specified by the command line argument '-t' or '--tool'.
The tool argument should be in the format 'tool_file:method_name' if a specific method is to
be executed. If no method is specified, the entire tool file is executed.

Additional arguments for the tool can be provided as command line arguments in the format
'--arg value'.

This file was made to be used as a replacement for poetry scripts. It is used by
[`go-task`](https://github.com/go-task/task) for executing tools on development environments.
"""

import argparse
import os
from importlib.util import module_from_spec, spec_from_file_location

TASKS_HOME = os.path.join(os.path.dirname(__file__), 'tasks')


def exec_tool(tool: str, args: dict = {}) -> None:
    tool_file, method_name = tool.split(':') if ':' in tool else (tool, None)
    spec = spec_from_file_location(tool_file, os.path.join(TASKS_HOME, f'{tool_file}.py'))

    if not spec or not spec.loader:
        raise Exception(f'Could not find tool file {tool_file} in {TASKS_HOME}')

    module = module_from_spec(spec)

    if method_name:
        spec.loader.exec_module(module)
        method = getattr(module, method_name, None)

        if not method:
            raise Exception(f'Could not find method {method_name} in {tool_file}')

        result = method(**args)
    else:
        result = spec.loader.exec_module(module) or 0

    exit(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute a tool')
    parser.add_argument('-t', '--tool', help='tool name', required=True)
    args, unknown_args = parser.parse_known_args()

    # convert unknown_args to dict to be used as kwargs for the tool
    tool_args = {
        unknown_args[i].lstrip('-'): unknown_args[i + 1] for i in range(0, len(unknown_args), 2)
    }

    tool = args.tool
    exec_tool(tool=args.tool, args=tool_args)
