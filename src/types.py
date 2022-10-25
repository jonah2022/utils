from pathlib import Path
from typing import Callable, Optional

PATH_TYPE = Path | str

FILTER_FUNC_TYPE = Callable[[str], str]
OPT_FILTER_FUNC_TYPE = Optional[FILTER_FUNC_TYPE]

NODE_TYPE = str
EDGE_TYPE = tuple[NODE_TYPE, NODE_TYPE]
GRAPH_TYPE = dict[NODE_TYPE, set[NODE_TYPE]]
