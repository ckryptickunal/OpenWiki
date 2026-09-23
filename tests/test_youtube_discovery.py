from openwiki.youtube import select_new_ids


def test_newest_first_stops_after_known_pages():
    pages = [
        ["new1", "new2"],
        ["old1", "old2"],
        ["old3"],
        ["should_not_see"],
    ]
    known = {"old1", "old2", "old3", "should_not_see"}
    assert select_new_ids(pages, known, stop_after_known_pages=2) == ["new1", "new2"]


def test_select_new_ids_skips_duplicates_inside_pages():
    pages = [["a", "a", "b"], ["b", "c"]]
    assert select_new_ids(pages, set()) == ["a", "b", "c"]
