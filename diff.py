import copy
from pathlib import Path

from src.dotfile import PydotWrapper

dotfile_directory = Path('data/10-10')
dotfile_paths = list(dotfile_directory.glob('*.dot'))

human_path = Path('data/10-10/10-10.txt')
human_path_total = Path('human_total.txt')
human_nodes = set()
with human_path.open('r', encoding='utf8') as f:
    for line in f:
        node, level = line.strip().split()
        human_nodes.add(node)
print(f'human node: {len(human_nodes)}')

total_human_nodes = dict()
with human_path_total.open('r', encoding='utf8') as f:
    for line in f:
        node, level = line.strip().split('\t')
        total_human_nodes[node] = level
print(f'total human node: {len(total_human_nodes)}')

for dotfile_path in dotfile_paths:
    wrapper = PydotWrapper.load_from_dotfile(dotfile_path)

    node_will_be_removed = []
    for node in wrapper.get_node_list():
        if node not in human_nodes:
            node_will_be_removed.append(node)
    print(
        f'number of nodes will be removed in human file: {len(node_will_be_removed)}'
    )
    target_path = dotfile_directory / f'{dotfile_path.name}(will_be_removed).txt'
    with target_path.open('w', encoding='utf8') as f:
        for node in node_will_be_removed:
            f.write(f'{node}\n')
    print(f'save to file: {target_path}')
    copied_wrapper = copy.deepcopy(wrapper)
    for node in node_will_be_removed:
        copied_wrapper.delete_node_(node)
    print(copied_wrapper.summary)

    node_not_contain = []
    for node in wrapper.get_node_list():
        if node not in total_human_nodes:
            node_not_contain.append(node)
    print(
        f'number of nodes not been contained in human file: {len(node_not_contain)}'
    )
    target_path = dotfile_directory / f'{dotfile_path.name}(not_contain).txt'
    with target_path.open('w', encoding='utf8') as f:
        for node in node_not_contain:
            f.write(f'{node}\n')
    print(f'save to file: {target_path}')

    node_contain_will_be_removed = []
    for node in wrapper.get_node_list():
        if node in total_human_nodes and node not in human_nodes:
            node_contain_will_be_removed.append(node)
    print(
        f'number of nodes been contained in human file but will be removed: {len(node_contain_will_be_removed)}'
    )
    target_path = dotfile_directory / f'{dotfile_path.name}(contain_will_be_removed).txt'
    with target_path.open('w', encoding='utf8') as f:
        for node in node_contain_will_be_removed:
            f.write(f'{node}\t{total_human_nodes[node]}\n')
    print(f'save to file: {target_path}')

    print('=' * 100)
    print(dotfile_path)
    print(
        f'node: {len(wrapper.get_node_list())}\n'
        f'node not contain: {len(node_not_contain)}\n'
        f'node will be removed: {len(node_will_be_removed)}\n'
        f'node contain but will be removed: {len(node_contain_will_be_removed)}\n'
        f'edge: {len(wrapper.get_edge_list())}\n'
        f'edge will be removed: {len(wrapper.get_edge_list()) - len(copied_wrapper.get_edge_list())}'
    )
    print('=' * 100)
