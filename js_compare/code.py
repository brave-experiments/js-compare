from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from networkx import read_graphml
from networkx.algorithms.similarity import graph_edit_distance

from js_compare.graphml import check_tool, install_tool, run_tool

if TYPE_CHECKING:
    from typing import IO, Any

@dataclass
class GraphSummary:
    edges: int
    nodes: int

@dataclass
class Comparison:
    code1: GraphSummary
    code2: GraphSummary
    distance: float
    normalized: float

def make_temp_file() -> IO[Any]:
    return NamedTemporaryFile(mode="w+", delete_on_close=False, encoding="utf8")

def compare(tool_dir: Path, code1: Path, code2: Path) -> Comparison:
    if not check_tool(tool_dir):
        install_tool(tool_dir)

    with make_temp_file() as file1, make_temp_file() as file2:
        graphml_str1 = run_tool(tool_dir, code1)
        assert graphml_str1
        file1.write(graphml_str1)
        file1.close()

        graphml_str2 = run_tool(tool_dir, code2)
        assert graphml_str2
        file2.write(graphml_str2)
        file2.close()

        g1 = read_graphml(Path(file1.name))
        g2 = read_graphml(Path(file2.name))

        g1_sum = GraphSummary(len(g1.edges), len(g1.nodes))
        g2_sum = GraphSummary(len(g2.edges), len(g2.nodes))
        distance = graph_edit_distance(g1, g2)
        max_elms = max(g1_sum.edges, g2_sum.edges) + max(g1_sum.nodes, g2_sum.nodes)
        norm_distance = distance / max_elms

        comparison = Comparison(g1_sum, g2_sum, distance, norm_distance)
        return comparison
