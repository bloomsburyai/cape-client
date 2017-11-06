import pytest
from .fixtures import cc


def test_get_default_message(cc):
    message = cc.get_default_message()
    assert message is not None


def test_set_default_message(cc):
    message = cc.set_default_message("Sorry! I don't know that.")
    assert message == "Sorry! I don't know that."
