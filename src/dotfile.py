from __future__ import annotations

import copy
import warnings
from pathlib import Path
from typing import Any, Sequence

import pydot

from .types import (EDGE_TYPE, GRAPH_TYPE, NODE_TYPE, OPT_FILTER_FUNC_TYPE,
                    PATH_TYPE)


class PydotWrapper:

    def __init__(self, graph: GRAPH_TYPE) -> None:
        self._graph = copy.deepcopy(graph)

    @classmethod
    def load_from_dotfile(
            cls,
            dotfile_path: PATH_TYPE,
            filter_func: OPT_FILTER_FUNC_TYPE = None) -> PydotWrapper:
        print(f'Trying to load from: {dotfile_path}')
        if isinstance(dotfile_path, str):
            dotfile_path = Path(dotfile_path)
        if filter_func is None:
            filter_func = cls._default_filter_func

        graph: GRAPH_TYPE = dict()
        with dotfile_path.open('r', encoding='utf8') as f:
            # TODO: only record node with edges
            for line in f:
                if '->' not in line:
                    continue
                source, target = map(filter_func, line.split('->'))
                if source in graph:
                    if target in graph[source]:
                        raise ValueError(f'Trying to add existing edge '
                                         f'`{source} -> {target}`')
                    graph[source].add(target)
                else:
                    graph[source] = {target}

        wrapper = cls(graph=graph)
        print(wrapper.summary)
        print('Done')

        return wrapper

    @classmethod
    def load_from_dotfiles(
            cls,
            dotfile_paths: Sequence[PATH_TYPE],
            filter_func: OPT_FILTER_FUNC_TYPE = None) -> list[PydotWrapper]:
        wrapper_list = []
        for dotfile_path in dotfile_paths:
            wrapper = cls.load_from_dotfile(dotfile_path=dotfile_path,
                                            filter_func=filter_func)
            wrapper_list.append(wrapper)

        return wrapper_list

    def merge_with(self, other: PydotWrapper) -> None:
        graph = self._graph
        other_graph = other.get_graph()

        for k, v in other_graph.items():
            if k in graph:
                graph[k] |= v
            else:
                graph[k] = v

    def remove_hanging_edges_(self) -> None:
        """Remove edges that at least one node does not exist"""
        prev_node_set = set(self._graph.keys())

        new_graph: GRAPH_TYPE = dict()
        for k, v in self._graph.items():
            new_graph[k] = set(filter(lambda x: x in prev_node_set, v))

        self._graph = new_graph

    def get_node_degrees(self) -> dict[NODE_TYPE, dict[str, int]]:
        degrees: dict[NODE_TYPE, dict[str, int]] = dict()

        for k, v in self._graph.items():
            try:
                degrees[k]['out'] += len(v)
            except KeyError:
                degrees[k] = {'out': len(v), 'in': 0}

            for node in v:
                try:
                    degrees[node]['in'] += 1
                except KeyError:
                    degrees[node] = {'out': 0, 'in': 1}

        return degrees

    def remove_nodes_with_zero_degree_(self) -> None:
        node_degrees = self.get_node_degrees()

        for k, v in node_degrees.items():
            if v['in'] + v['out'] == 0:
                self.delete_node_(k)

    def fix_hanging_edges_(self) -> None:
        """Add nodes that does not exist in edges"""
        prev_node_set = set(self._graph.keys())
        new_node_set: set[NODE_TYPE] = set()

        for v in self._graph.values():
            new_node_set.update(filter(lambda x: x not in prev_node_set, v))

        new_graph = self.get_graph()
        for node in new_node_set:
            new_graph[node] = set()

        self._graph = new_graph

    def __or__(self, other: PydotWrapper) -> PydotWrapper:
        wrapper = copy.deepcopy(self)
        wrapper.merge_with(other)

        return wrapper

    def get_graph(self) -> GRAPH_TYPE:
        return copy.deepcopy(self._graph)

    def get_edge_list(self) -> list[EDGE_TYPE]:
        edge_list: list[EDGE_TYPE] = []
        for k, v in self._graph.items():
            edge_list.extend(map(lambda x: (k, x), v))
        return edge_list

    def get_node_list(self) -> list[NODE_TYPE]:
        return list(self._graph.keys())

    def get_node_edge_list(self, node: NODE_TYPE) -> list[NODE_TYPE]:
        if node not in self._graph:
            raise ValueError('Graph does not have node `{node}`')
        return list(self._graph[node])

    def delete_node_(self, node: NODE_TYPE) -> None:
        if node not in self._graph:
            warnings.warn('Graph does not have node `{node}`')
            return

        self._graph.pop(node)
        for node_set in self._graph.values():
            if node in node_set:
                node_set.remove(node)

    def delete_nodes_(self, node_seq: Sequence[NODE_TYPE]) -> None:
        for node in set(node_seq):
            self.delete_node_(node)

    def delete_edges_(self, edge_list: list[EDGE_TYPE]) -> None:
        for u, v in edge_list:
            if u not in self._graph:
                warnings.warn(f'Graph does not have node `{u}`')
            else:
                if v in self._graph[u]:
                    self._graph[u].remove(v)

    def get_sub_wrapper(self, node_seq: Sequence[NODE_TYPE]) -> PydotWrapper:
        sub_graph: GRAPH_TYPE = dict()

        node_set = set(node_seq)
        # check if node not in original graph
        for node in node_set:
            if node not in self._graph:
                warnings.warn(f'Node `{node}` not in graph')
                sub_graph[node] = set()

        for k, v in self._graph.items():
            if k not in node_set:
                continue
            sub_graph[k] = set(filter(lambda x: x in node_set, v))

        return PydotWrapper(sub_graph)

    @staticmethod
    def _default_filter_func(s: str) -> str:
        return s.strip().strip('\'\"‘’“”;；')

    def to_pydot(self) -> pydot.Dot:
        edge_list = self.get_edge_list()

        dot = pydot.graph_from_edges(edge_list, directed=True)
        for node in self.get_node_list():
            dot.add_node(pydot.Node(node))

        return dot

    @property
    def summary(self) -> dict[str, Any]:
        return {
            'node number': len(self._graph.keys()),
            'edge number': len(self.get_edge_list())
        }
