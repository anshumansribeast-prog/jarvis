import os

import file_controller


def test_create_folder_on_desktop(isolated_home):
    _home, folders = isolated_home
    path = file_controller.create_folder("notes")
    assert path == os.path.join(folders["desktop"], "notes")
    assert os.path.isdir(path)


def test_create_file_adds_txt_when_no_extension(isolated_home):
    path = file_controller.create_file("todo")
    assert path.endswith("todo.txt")
    assert os.path.isfile(path)


def test_find_matches_substring_shortest_first(isolated_home):
    _home, folders = isolated_home
    file_controller.create_file("alpha-report.txt")
    nested = os.path.join(folders["documents"], "reports")
    os.makedirs(nested)
    with open(os.path.join(nested, "alpha-report-long.txt"), "w", encoding="utf-8"):
        pass
    matches = file_controller.find("alpha-report", root=str(_home))
    assert matches
    assert os.path.basename(matches[0]) == "alpha-report.txt"


def test_read_text_file_truncates(isolated_home):
    path = file_controller.create_file("story.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("a" * 50)
    content, truncated = file_controller.read_text_file(path, max_chars=20)
    assert content == "a" * 20
    assert truncated is True


def test_rename_and_delete_file(isolated_home):
    path = file_controller.create_file("old.txt")
    renamed = file_controller.rename(path, "new.txt")
    assert os.path.basename(renamed) == "new.txt"
    assert os.path.isfile(renamed)
    file_controller.delete(renamed)
    assert not os.path.exists(renamed)


def test_move_into_known_folder(isolated_home):
    _home, folders = isolated_home
    path = file_controller.create_file("photo.txt")
    moved = file_controller.move(path, "pictures")
    assert moved == os.path.join(folders["pictures"], "photo.txt")
    assert os.path.isfile(moved)


def test_move_unknown_folder_returns_none(isolated_home):
    path = file_controller.create_file("stay.txt")
    assert file_controller.move(path, "nowhere") is None
    assert os.path.isfile(path)


def test_delete_folder(isolated_home):
    path = file_controller.create_folder("scratch")
    file_controller.delete(path)
    assert not os.path.exists(path)
