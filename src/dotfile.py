from __future__ import annotations

import copy
from pathlib import Path
from typing import Callable, Optional, Sequence

import pydot

PATH_TYPE = Path | str

FILTER_FUNC_TYPE = Callable[[str], str]
OPT_FILTER_FUNC_TYPE = Optional[FILTER_FUNC_TYPE]

NODE_TYPE = str
EDGE_TYPE = tuple[NODE_TYPE, NODE_TYPE]
GRAPH_TYPE = dict[NODE_TYPE, set[NODE_TYPE]]


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
    def summary(self) -> dict:
        return {
            'node number': len(self._graph.keys()),
            'edge number': len(self.get_edge_list())
        }


if __name__ == '__main__':
    import functools
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--dotfile_paths',
                        '-dp',
                        type=Path,
                        nargs='+',
                        help='Paths of dotfile')
    parser.add_argument('--dotfile_directory',
                        '-dd',
                        type=Path,
                        help='Directory of dotfiles')
    parser.add_argument('--merged_dotfile_path',
                        '-mdp',
                        type=Path,
                        required=True,
                        help='Path of merged dotfile')

    args = parser.parse_args()
    if args.dotfile_paths is not None and args.dotfile_directory is not None:
        raise ValueError('Argument `dotfile_paths` and `dotfile_directory` '
                         'can not be set both')
    if args.dotfile_paths is None and args.dotfile_directory is None:
        raise ValueError('Argument `dotfile_paths` and `dotfile_directory` '
                         'can not be both None')

    if args.dotfile_paths is not None:
        dotfile_paths = args.dotfile_paths
    else:
        dotfile_paths = list(args.dotfile_directory.glob('*.dot'))

    if len(dotfile_paths) == 0:
        raise ValueError('At least one dotfile path should be set')
    for dp in dotfile_paths:
        if not dp.exists():
            raise ValueError(f'Path `{dp}` is not exist')

    wrapper_list = PydotWrapper.load_from_dotfiles(dotfile_paths)
    merged_wrapper = functools.reduce(lambda x, y: x | y, wrapper_list)
    print(f'Summary of merged dot: {merged_wrapper.summary}')

    dot = merged_wrapper.to_pydot()
    dot.write_raw(args.merged_dotfile_path)
