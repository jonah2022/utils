if __name__ == '__main__':
    import functools
    from argparse import ArgumentParser
    from pathlib import Path

    from src import PydotWrapper

    parser = ArgumentParser()
    parser.add_argument('--dotfile_paths',
                        '-dp',
                        type=Path,
                        nargs='+',
                        help='Paths of dotfile')
    parser.add_argument('--dotfile_directory',
                        '-dd',
                        type=Path,
                        help='Base directory of dotfiles')
    parser.add_argument('--merged_dotfile_path',
                        '-mdp',
                        type=Path,
                        required=True,
                        help='Path of merged dotfile')
    parser.add_argument(
        '--removing_hanging_edges',
        '-rhe',
        action='store_true',
        help='Remove edges that at least one node does not exist')
    parser.add_argument('--fix_hanging_edges',
                        '-fhe',
                        action='store_true',
                        help='Add nodes that does not exist in edges')
    parser.add_argument('--remove_nodes_without_edges',
                        '-rnwe',
                        action='store_true',
                        help='Remove nodes ')

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
