import pytest
from cape.client import CapeClient
from cape.client import CapeException


def test_saved_replies():
    cc = CapeClient()
    cc.login('blo', 'bla')
    saved_replies = cc.get_saved_replies()
    assert 'totalItems' in saved_replies
    assert 'items' in saved_replies


def test_saved_replies_number_of_items():
    cc = CapeClient()
    cc.login('blo', 'bla')
    saved_replies = cc.get_saved_replies(number_of_items=1)
    assert len(saved_replies['items']) == 1
    saved_replies = cc.get_saved_replies(number_of_items=2)
    assert len(saved_replies['items']) == 2


def test_saved_replies_offset():
    cc = CapeClient()
    cc.login('blo', 'bla')
    item1 = cc.get_saved_replies(number_of_items=1)['items'][0]
    item2 = cc.get_saved_replies(number_of_items=1, offset=1)['items'][0]
    assert item1 != item2


def test_create_saved_reply():
    cc = CapeClient()
    cc.login('blo', 'bla')
    reply_id = cc.create_saved_reply('What colour is the sky?', 'Blue')
    assert reply_id is not None


def test_delete_saved_reply():
    cc = CapeClient()
    cc.login('blo', 'bla')
    reply_id = cc.delete_saved_reply(52)
    assert reply_id == '52'
