from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import copyfile
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from networkx import read_graphml

from js_compare.ast_tree import ASTTree
from js_compare.graphml import check_tool, install_tool, run_tool

if TYPE_CHECKING:
    from typing import Any, IO

    import networkx
    from networkx.classes.graph import _Node

    from js_compare.types import AstNodeType

@dataclass
class Comparison:
    graph1: int
    graph2: int
    # Number of nodes in subtrees that appear in graph1 that also appear in
    # graph2
    overlap: int
    # % of nodes in graph1 that appear in identical subtrees in graph2
    normalized: float

def make_temp_file() -> IO[Any]:
    return NamedTemporaryFile(mode="w+", delete_on_close=False, encoding="utf8")

def compare_graphs(graph1: networkx, graph2: networkx) -> Comparison:
    tree1 = ASTTree(graph1)
    tree2 = ASTTree(graph2)

    overlap_nodes = 0
    if __debug__:
        observed_subtree_roots: set[_Node] = set()
    for common_subtree_root in tree1.common_subtree_roots(tree2):
        if __debug__:
            assert common_subtree_root.node not in observed_subtree_roots
            observed_subtree_roots.add(common_subtree_root.node)
        overlap_nodes += common_subtree_root.weight

    normalized = overlap_nodes / float(tree1.num_nodes())
    comparison = Comparison(len(graph1), len(graph2), overlap_nodes, normalized)
    return comparison

def compare_code(tool_dir: Path, code1: Path, code2: Path,
                 node_types: list[AstNodeType]) -> Comparison:
    if not check_tool(tool_dir):
        install_tool(tool_dir)

    with make_temp_file() as file1, make_temp_file() as file2:
        graphml_str1 = run_tool(tool_dir, code1, node_types)
        assert graphml_str1
        file1.write(graphml_str1)
        file1.close()

        graphml_str2 = run_tool(tool_dir, code2, node_types)
        assert graphml_str2
        file2.write(graphml_str2)
        file2.close()

        copyfile(file1.name, "/tmp/graph1.graphml")
        copyfile(file2.name, "/tmp/graph2.graphml")

        g1 = read_graphml(Path(file1.name))
        g2 = read_graphml(Path(file2.name))
        return compare_graphs(g1, g2)
