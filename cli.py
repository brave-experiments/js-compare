#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
from typing import TYPE_CHECKING

from js_compare.consts import GRAPHML_TOOL_PATH
from js_compare.code import compare

if TYPE_CHECKING:
    from js_compare.code import Comparison

if len(sys.argv) < 3:
    sys.stderr.write("Usage: cli.py [file] [file]\n")
    sys.exit(1)

file1 = Path(sys.argv[1])
file2 = Path(sys.argv[2])

result: Comparison = compare(GRAPHML_TOOL_PATH, file1, file2)
print("graph1 #edges:\t" + str(result.code1.edges))
print("graph1 #nodes:\t" + str(result.code1.nodes))
print("graph2 #edges:\t" + str(result.code2.edges))
print("graph2 #nodes:\t" + str(result.code2.nodes))
print("distance:\t" + str(result.distance))
print("normalized:\t" + str(result.normalized))
