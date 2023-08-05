# -*- coding: utf-8 -*-
"""
Filesystem-related utilities.
"""
import os


def path_to_module_name(filename):
    """Convert a path to a file to a Python module name."""

    filename = os.path.relpath(filename)

    dotted_path = []
    while True:
        filename, component = os.path.split(filename)
        dotted_path.insert(0, component)
        if filename == "":
            break

    dotted_path[-1] = os.path.splitext(dotted_path[-1])[0]
    if dotted_path[-1] == "__init__":
        dotted_path.pop()

    return ".".join(dotted_path)
