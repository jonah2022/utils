from src import PydotWrapper


def test_merge_with() -> None:
    dotfile1 = 'tests/data/1.dot'
    dotfile2 = 'tests/data/2.dot'

    wrapper1 = PydotWrapper.load_from_dotfile(dotfile1)
    assert wrapper1.get_graph() == {'a': {'b', 'c'}, 'b': {'c'}}

    wrapper2 = PydotWrapper.load_from_dotfile(dotfile2)
    assert wrapper2.get_graph() == {'a': {'b', 'c'}, 'b': {'a'}, 'c': {'a'}}

    merged_wrapper = wrapper1 | wrapper2
    assert merged_wrapper.get_graph() == {
        'a': {'b', 'c'},
        'b': {'a', 'c'},
        'c': {'a'}
    }
