import pytest
from cape.client import CapeClient
from cape.client import CapeException
from .fixtures import cc


def test_inbox(cc):
    inbox = cc.get_inbox()
    assert 'totalItems' in inbox
    assert 'items' in inbox


def test_inbox_number_of_items(cc):
    inbox = cc.get_inbox(number_of_items=1)
    assert len(inbox['items']) == 1
    inbox = cc.get_inbox(number_of_items=2)
    assert len(inbox['items']) == 2


def test_inbox_offset(cc):
    item1 = cc.get_inbox(number_of_items=1)['items'][0]
    item2 = cc.get_inbox(number_of_items=1, offset=1)['items'][0]
    assert item1 != item2


def test_mark_inbox_read(cc):
    inbox_id = cc.mark_inbox_read(12)
    assert inbox_id == '12'


def test_archive_inbox(cc):
    inbox_id = cc.archive_inbox(15)
    assert inbox_id == '15'


def test_inbox_read(cc):
    items = cc.get_inbox(read=True)
    for item in items['items']:
        assert item['read']
    items = cc.get_inbox(read=False)
    for item in items['items']:
        assert not item['read']


def test_inbox_answered(cc):
    items = cc.get_inbox(answered=True)
    for item in items['items']:
        assert item['answered']
    items = cc.get_inbox(answered=False)
    for item in items['items']:
        assert not item['answered']