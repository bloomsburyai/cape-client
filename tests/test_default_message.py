import pytest
from cape.client import CapeClient
from cape.client import CapeException


def test_get_default_message():
    cc = CapeClient()
    cc.login('blo', 'bla')
    message = cc.get_default_message()
    assert message is not None


def test_set_default_message():
    cc = CapeClient()
    cc.login('blo', 'bla')
    message = cc.set_default_message("Sorry! I don't know that.")
    assert message == "Sorry! I don't know that."
