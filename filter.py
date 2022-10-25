from pathlib import Path

from src.dotfile import PydotWrapper

input_file_path = Path('input_10-25.txt')
human_file_path = r'human_10-25.txt'

wrapper = PydotWrapper.load_from_dotfile(input_file_path)
wrapper.remove_hanging_edges_()
wrapper.remove_nodes_with_zero_degree_()
input_nodes = set(wrapper.get_node_list())

human_nodes2level = dict()
with open(human_file_path, 'r', encoding='utf8') as f:
    for line in f:
        node, level = line.split()
        human_nodes2level[node] = int(level)

human_nodes = set(human_nodes2level.keys())

print(f'original input node number: {len(input_nodes)}')
print(f'original human node number: {len(human_nodes)}')

both_nodes = human_nodes & input_nodes
print(f'both node number: {len(both_nodes)}')

only_input_nodes = input_nodes - both_nodes
with open('node_have_no_level.txt', 'w', encoding='utf8') as f:
    for node in only_input_nodes:
        f.write(node)
        f.write('\n')

removed_edges = []
filter_input_graph = dict()
for node, edges in wrapper.get_graph().items():
    if node not in both_nodes:
        removed_edges.extend([(node, v)
                              for v in wrapper.get_node_edge_list(node)])
        continue
    filtered_edges = edges & both_nodes
    removed_edges.extend([(node, v) for v in edges - both_nodes])
    filter_input_graph[node] = filtered_edges

with open(f'edges_will_be_removed_{human_file_path}', 'w',
          encoding='utf8') as f:
    for u, v in removed_edges:
        f.write(f'{u} -> {v}\n')

filter_wrapper = PydotWrapper(filter_input_graph)
wrapper.remove_hanging_edges_()
wrapper.remove_nodes_with_zero_degree_()
print(filter_wrapper.summary)
filter_dot = filter_wrapper.to_pydot()
filter_dot.write_raw(f'filtered_{input_file_path.name}')

human_node_level_list = sorted(human_nodes2level.items(), key=lambda x: x[1])
with open(f'filtered_{input_file_path.name.replace("input", "human")}',
          'w',
          encoding='utf8') as f:
    for node, level in human_node_level_list:
        if node not in both_nodes:
            continue
        f.write(f'{node}\t{level}\n')
