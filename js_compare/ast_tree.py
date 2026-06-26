from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from operator import attrgetter
from typing import TYPE_CHECKING
import sys

from networkx import DiGraph, dag_longest_path

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Final, Literal, Optional

    from networkx.classes.graph import _Node

ATTR_DIGEST: Final = "digest"
ATTR_LABEL: Final = "label"
ATTR_WEIGHT: Final = "weight"
type GraphAttr = Literal["digest", "label", "weight"]
type Digest = str

@dataclass
class NodeAttrs:
    digest: Digest
    label: str
    node: _Node
    weight: int

def get_attrs_for_node(graph: DiGraph, node: _Node) -> NodeAttrs:
    assert node in graph.nodes
    raw_attrs = graph.nodes[node]
    label = raw_attrs[ATTR_LABEL]
    assert isinstance(label, str)
    try:
        digest = raw_attrs[ATTR_DIGEST]
        assert isinstance(digest, str)
        weight = raw_attrs[ATTR_WEIGHT]
        assert isinstance(weight, int)
        return NodeAttrs(digest, label, node, weight)
    except KeyError:
        weight = 1
        hasher = sha256()
        hasher.update(label.encode("utf8"))
        for child_node in graph.neighbors(node):
            child_attrs = get_attrs_for_node(graph, child_node)
            weight += child_attrs.weight
            hasher.update(child_attrs.digest.encode("utf8"))
        digest = hasher.hexdigest()
        raw_attrs[ATTR_DIGEST] = digest
        raw_attrs[ATTR_WEIGHT] = weight
        return NodeAttrs(digest, label, node, weight)

def remove_node_for_graph(graph: DiGraph, node: _Node,
                          update: bool=False) -> int:
    num_initial_nodes = len(graph)
    num_nodes_removed = 0
    child_nodes = list(graph.neighbors(node))
    for child_node in child_nodes:
        num_nodes_removed += remove_node_for_graph(graph, child_node, False)
    parent_nodes = graph.predecessors(node)

    graph.remove_node(node)
    num_nodes_removed += 1

    if not update:
        return num_nodes_removed

    # pylint: disable=while-used
    while len(parent_nodes) == 1:
        parent_node = parent_nodes[0]
        del graph[parent_node][ATTR_DIGEST]
        del graph[parent_node][ATTR_WEIGHT]
        get_attrs_for_node(graph, parent_node)
        parent_nodes = graph.predecessors(parent_node)

    # Check that the number of nodes in the graph after we do the removal
    # matches the number of nodes that were in the graph at the start,
    # less the number of removed nodes.
    assert len(graph) == num_initial_nodes - num_nodes_removed
    return num_nodes_removed

def nodes_with_attr(graph: DiGraph, key: GraphAttr,
                    value: Optional[str]=None) -> Generator[_Node]:
    if not value:
        return (n for n, attr in graph.nodes(data=key))
    return (n for n, attr in graph.nodes(data=True) if attr.get(key) == value)

def _subtree_as_set(graph: DiGraph, node: _Node) -> set[_Node]:
    subtree_set: set[_Node] = set()
    subtree_set.add(node)
    for child_node in graph.neighbors(node):
        child_subgraph_set = _subtree_as_set(graph, child_node)
        assert subtree_set.isdisjoint(child_subgraph_set)
        subtree_set |= child_subgraph_set
    return subtree_set


class ASTTree:
    graph: DiGraph
    root: _Node

    def __init__(self, graph: DiGraph, root_node: Optional[_Node]=None):
        """Initializer, external callers should leave root_node as None.
        The root_node param should only be used by the copy() method,
        to avoid a bunch of unnecessary work."""
        if root_node:
            self.graph = graph
            self.root = root_node
        else:
            root_nodes = nodes_with_attr(graph, ATTR_LABEL, "Program")
            self.root = next(root_nodes)
            assert next(root_nodes, None) is None
            self.graph = graph.copy()
            current_recursion_limit = sys.getrecursionlimit()
            longest_path = dag_longest_path(self.graph)
            if len(longest_path) > current_recursion_limit:
                sys.setrecursionlimit(len(longest_path) * 2)
            get_attrs_for_node(self.graph, self.root)
            sys.setrecursionlimit(current_recursion_limit)

    def copy(self) -> ASTTree:
        return ASTTree(self.graph, self.root)

    def attrs_for_node(self, node: _Node) -> NodeAttrs:
        return get_attrs_for_node(self.graph, node)

    def remove_node(self, node: _Node, update: bool=False) -> int:
        return remove_node_for_graph(self.graph, node, update)

    def num_nodes(self) -> int:
        return len(self.graph)

    def nodes_with_attr(self, attr: GraphAttr,
                        value: Optional[str]=None) -> Generator[NodeAttrs]:
        for n in nodes_with_attr(self.graph, attr, value):
            yield self.attrs_for_node(n)

    def nodes_sorted(self, key: GraphAttr,
                     reverse: bool=False) -> list[NodeAttrs]:
        nodes = list(self.nodes_with_attr(key))
        return sorted(nodes, key=attrgetter(key), reverse=reverse)

    def contains(self, digest: Digest) -> list[NodeAttrs]:
        return list(self.nodes_with_attr(ATTR_DIGEST, digest))

    def common_subtree_roots(self, tree: ASTTree,  minimum: int) -> Generator[NodeAttrs]:
        """Return NodeAttrs that are roots of subtrees that appear in
        the current instance, and also the remote instance (uniquely)."""
        other_tree = tree.copy()
        if __debug__:
            prev_observed_weight: int | None = None
            prev_tree_size = other_tree.num_nodes()

        unmatched_nodes: set[_Node] = set(list(self.graph.nodes))
        matched_nodes: set[_Node] = set()

        for node_attrs in self.nodes_sorted(ATTR_WEIGHT, True):
            if node_attrs.weight < minimum:
                # Since nodes are ordered by weight, the moment we hit the first
                # node (i.e., subtree root) with a weight below the given
                # threshold, we can stop looking.
                break

            if node_attrs.node in matched_nodes:
                continue

            if __debug__:
                # Check to make sure we're actually looking at nodes
                # ordered largest to smallest subtrees.
                if prev_observed_weight is None:
                    prev_observed_weight = node_attrs.weight
                else:
                    assert prev_observed_weight >= node_attrs.weight
                    prev_observed_weight = node_attrs.weight

            matches = other_tree.contains(node_attrs.digest)
            if len(matches) == 0:
                continue

            removed_node_attrs: NodeAttrs = matches[0]
            num_removed_nodes = other_tree.remove_node(removed_node_attrs.node)
            assert num_removed_nodes == removed_node_attrs.weight

            matched_local_subtree = _subtree_as_set(self.graph, node_attrs.node)
            assert len(matched_local_subtree) == num_removed_nodes
            matched_nodes |= matched_local_subtree
            unmatched_nodes = unmatched_nodes - matched_local_subtree

            if __debug__:
                # Check to make sure we're never revisiting the same nodes
                # in the local graph (i.e., we're not double counting
                # any nodes in the local graph as overlapping with the
                # remote graph).
                local_subtree = _subtree_as_set(self.graph, node_attrs.node)
                assert local_subtree.isdisjoint(matched_nodes)
                matched_nodes |= local_subtree

                # Also check to make sure that the new size of the graph is
                # equal to i. the size of the graph before we removed the
                # common subtree (`prev_tree_size``), less ii. the
                # number of nodes in the common subtree we just removed.
                cur_tree_size = other_tree.num_nodes()
                assert cur_tree_size == prev_tree_size - num_removed_nodes
                prev_tree_size = cur_tree_size

            yield removed_node_attrs
