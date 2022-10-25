from .types import GRAPH_TYPE


def get_sccs_by_tarjan(graph: GRAPH_TYPE):
    dfn: dict[str, int] = dict()
    low: dict[str, int] = dict()
    st: list[str] = []
    vis: set[str] = set()
    depth: int = 0
    sccs: list[list[str]] = []

    def dfs(u: str) -> None:
        nonlocal depth
        depth += 1

        dfn[u] = depth
        low[u] = depth
        vis.add(u)
        st.append(u)

        for v in graph[u]:
            if v not in dfn:
                dfs(v)
                low[u] = min(low[u], low[v])
            else:
                if v in vis:
                    low[u] = min(low[u], low[v])

        if dfn[u] == low[u]:
            scc = [u]
            vis.remove(u)

            while st[-1] != u:
                scc.append(st[-1])
                vis.remove(st[-1])
                st.pop()
            st.pop()

            sccs.append(scc)

    for u in graph.keys():
        if u not in dfn:
            dfs(u)

    return sccs


if __name__ == '__main__':
    import json
    from copy import deepcopy
    from pathlib import Path

    from .dotfile import PydotWrapper

    dot_path = 'data/human_merged.txt'
    pydot_wrapper = PydotWrapper.load_from_dotfile(dot_path)

    copied_pydot_wrapper = deepcopy(pydot_wrapper)
    copied_pydot_wrapper.fix_hanging_edges_()
    print(copied_pydot_wrapper.summary)

    copied_pydot_wrapper = deepcopy(pydot_wrapper)
    copied_pydot_wrapper.remove_hanging_edges_()
    print(copied_pydot_wrapper.summary)

    pydot_wrapper.fix_hanging_edges_()
    anchors = [
        'acl',
        'attr',
        'audit',
        'bash',
        'bzip2',
        'cryptsetup',
        'dbus',
        'efibootmgr',
        'efivar',
        'elfutils',
        'gawk',
        'glibc',
        'gmp',
        'gnutls',
        'grep',
        'grub2',
        'kexec-tools',
        'kmod',
        'libcap',
        'libcap-ng',
        'libgcrypt',
        'libgpg-error',
        'libidn2',
        'libseccomp',
        'libselinux',
        'libxcrypt',
        'linux-firmware',
        'lz4',
        'microcode_ctl',
        'openssl',
        'pam',
        'sed',
        'texinfo',
        'util-linux',
        'xz',
        'zlib',
    ]
    pydot_wrapper.delete_nodes_(anchors)
    print(pydot_wrapper.summary)
    sccs = get_sccs_by_tarjan(pydot_wrapper.get_graph())

    filtered_sccs = []
    threshold = 2
    for scc in sccs:
        if len(scc) >= threshold:
            filtered_sccs.append(scc.copy())

    data_dir: Path = Path('data')
    work_dir = data_dir / 'cycles_with_anchors'
    if not work_dir.exists():
        work_dir.mkdir(parents=True)

    summary = dict()
    for i, scc in enumerate(filtered_sccs, start=1):
        sub_dot_name = f'cycle_{i}.dot'
        sub_wrapper = pydot_wrapper.get_sub_wrapper(scc)
        summary[sub_dot_name] = sub_wrapper.summary

        sub_pydot = sub_wrapper.to_pydot()
        sub_pydot.write_raw(work_dir / sub_dot_name)

    summary['anchors'] = anchors
    with open(work_dir / 'summary.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(summary))

    # delete edges
    scc = filtered_sccs[0]
    sub_wrapper = pydot_wrapper.get_sub_wrapper(scc)
    deleted_edges = []
    for u, v in sub_wrapper.get_edge_list():
        if ('perl' in u and 'perl' not in v) or ('perl' not in u
                                                 and 'perl' in v):
            deleted_edges.append((u, v))

    sub_wrapper.delete_edges_(deleted_edges)
    sccs = get_sccs_by_tarjan(sub_wrapper.get_graph())

    filtered_sccs = []
    threshold = 2
    for scc in sccs:
        if len(scc) >= threshold:
            filtered_sccs.append(scc.copy())

    data_dir: Path = Path('data')
    work_dir = data_dir / 'broken_cycles'
    if not work_dir.exists():
        work_dir.mkdir(parents=True)

    summary = dict()
    for i, scc in enumerate(filtered_sccs, start=1):
        sub_dot_name = f'cycle_{i}.dot'
        sub_wrapper = pydot_wrapper.get_sub_wrapper(scc)
        summary[sub_dot_name] = sub_wrapper.summary

        sub_pydot = sub_wrapper.to_pydot()
        sub_pydot.write_raw(work_dir / sub_dot_name)

    summary['anchors'] = anchors
    with open(work_dir / 'summary.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(summary))
