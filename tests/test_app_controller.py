import app_controller


def test_resolve_app_exact_key():
    entry = app_controller.resolve_app("notepad")
    assert entry is not None
    assert entry["process_name"] == "notepad.exe"


def test_resolve_app_substring_either_way():
    assert app_controller.resolve_app("vs code")["process_name"] == "Code.exe"
    assert app_controller.resolve_app("code")["process_name"] == "Code.exe"


def test_resolve_app_unknown_returns_none():
    assert app_controller.resolve_app("photoshop") is None


def test_launch_app_unknown_returns_false():
    assert app_controller.launch_app("not-an-app") is False


def test_close_app_unknown_returns_false():
    assert app_controller.close_app("not-an-app") is False
