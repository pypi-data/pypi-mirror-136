from src import say_hello


def test_main_no_params():
    assert say_hello() == "Hello World!"


def test_main_with_params():
    assert say_hello("Everybody") == "Hello Everybody!"
