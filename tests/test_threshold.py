import pytest
from cape.client import CapeClient
from cape.client import CapeException
from .fixtures import cc


def test_get_default_threshold(cc):
    threshold = cc.get_default_threshold()
    assert threshold in ['low', 'medium', 'high']


def test_set_default_threshold(cc):
    threshold = cc.set_default_threshold('low')
    assert threshold == 'low'
