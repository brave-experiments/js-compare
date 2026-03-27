from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from networkx import read_graphml, laplacian_spectrum
from networkx.algorithms.similarity import graph_edit_distance
import numpy as np

from js_compare.graphml import check_tool, install_tool, run_tool

if TYPE_CHECKING:
    from typing import Any, IO

    import networkx

    from js_compare.types import AstNodeType

@dataclass
class GraphSummary:
    edges: int
    nodes: int

@dataclass
class Comparison:
    code1: GraphSummary
    code2: GraphSummary
    distance: float

def make_temp_file() -> IO[Any]:
    return NamedTemporaryFile(mode="w+", delete_on_close=False, encoding="utf8")

def normalized_edit_distance(graph1: networkx, graph2: networkx) -> float:
    max_elms = max(len(graph1), len(graph2))
    distance = graph_edit_distance(graph1, graph2)
    assert isinstance(distance, float)
    return distance / max_elms

def normalized_spectral_distance(graph1: networkx, graph2: networkx) -> float:
    # 1. Get spectra
    spec1 = laplacian_spectrum(graph1)
    spec2 = laplacian_spectrum(graph2)

    # 2. Normalize by node count (scale values to [0, 1] range)
    # This makes the 'shape' comparable regardless of graph size
    spec1 = spec1 / len(graph1)
    spec2 = spec2 / len(graph2)

    # 3. Pad the smaller spectrum with zeros
    # (Required to compare vectors of different lengths)
    max_len = max(len(spec1), len(spec2))
    spec1_padded = np.pad(np.sort(spec1), (0, max_len - len(spec1)))
    spec2_padded = np.pad(np.sort(spec2), (0, max_len - len(spec2)))

    # 4. Calculate Euclidean distance and divide by max_len
    # Dividing by max_len ensures the distance doesn't just grow with N
    distance = np.linalg.norm(spec1_padded - spec2_padded) / np.sqrt(max_len)
    assert isinstance(distance, float)
    return distance

def compare_graphs(graph1: networkx, graph2: networkx,
                   exact: bool=False) -> Comparison:
    g1_sum = GraphSummary(len(graph1.edges), len(graph1.nodes))
    g2_sum = GraphSummary(len(graph2.edges), len(graph2.nodes))

    if exact:
        distance = normalized_edit_distance(graph1, graph2)
    else:
        distance = normalized_spectral_distance(graph1, graph2)

    comparison = Comparison(g1_sum, g2_sum, distance)
    return comparison

def compare(tool_dir: Path, code1: Path, code2: Path,
            node_types: list[AstNodeType], exact: bool=False) -> Comparison:
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

        g1 = read_graphml(Path(file1.name))
        g2 = read_graphml(Path(file2.name))
        return compare_graphs(g1, g2, exact)
