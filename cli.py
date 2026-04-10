#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING

from js_compare.compare import compare_code
from js_compare.consts import GRAPHML_TOOL_PATH
from js_compare.filetype import FileType
from js_compare.types import ast_node_types

if TYPE_CHECKING:
    from js_compare.types import AstNodeType

loose_options: list[AstNodeType] = [
    "Programs",
    "Functions",
    "Declarations",
    "Statements",
]
ast_options = [
    "all",
    "loose",
    *ast_node_types
]

parser = argparse.ArgumentParser(
    prog="js-compare",
    description="Compares JavaScript code units, based on their AST",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-o", "--output",
    default="-",
    help="Path to write comparison results to. Use '-' to write results to "
         "STDOUT.",
    type=FileType("w", encoding="utf-8"))
parser.add_argument("-t", "--types",
    choices=ast_options,
    default=["loose"],
    help="Which AST nodes to include in the code graph when comparing code "
         "units. You can also use the special cases 'all' to "
         "include all AST nodes, or 'loose', to include just the following "
         "node types: " + ", ".join(loose_options),
    nargs="+")
parser.add_argument("-w", "--workspace",
    default=GRAPHML_TOOL_PATH,
    help="Path to a directory that exists and be written to, or does not "
         "exist and can be created. This directory will be used to create a "
         "child program to convert JavaScript code to GraphML.",)
parser.add_argument("file1",
    help="Path to first JavaScript code unit to compare.",
    type=Path)
parser.add_argument("file2",
    help="Path to first JavaScript code unit to compare.",
    type=Path)

args = parser.parse_args()

if "loose" in args.types:
    if len(args.types) > 1:
        raise argparse.ArgumentTypeError(
            "Invalid arguments for --type: Cannot use 'loose' preset type "
            "along with other types.")
    NODE_TYPES = loose_options
elif "all" in args.types:
    if len(args.types) > 1:
        raise argparse.ArgumentTypeError(
            "Invalid arguments for --type: Cannot use 'all' preset type "
            "along with other types.")
    NODE_TYPES = ast_node_types
else:
    NODE_TYPES = args.types

result = compare_code(args.workspace, args.file1, args.file2, NODE_TYPES)
data = {
    "code1": result.graph1,
    "code2": result.graph2,
    "overlap": result.overlap,
    "normalized": result.normalized,
}
json.dump(data, args.output)
args.output.write("\n")
