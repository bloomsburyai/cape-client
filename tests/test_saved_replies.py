import pytest
from cape.client import CapeClient
from cape.client import CapeException
from .fixtures import cc


def test_saved_replies(cc):
    saved_replies = cc.get_saved_replies()
    assert 'totalItems' in saved_replies
    assert 'items' in saved_replies


def test_saved_replies_ids(cc):
    saved_replies = cc.get_saved_replies(saved_reply_ids=["d27b6282-c3c3-11e7-8d29-d15d28ee5381"])
    assert len(saved_replies['items']) == 1


def test_saved_replies_number_of_items(cc):
    saved_replies = cc.get_saved_replies(number_of_items=1)
    assert len(saved_replies['items']) == 1
    saved_replies = cc.get_saved_replies(number_of_items=2)
    assert len(saved_replies['items']) == 2


def test_saved_replies_offset(cc):
    item1 = cc.get_saved_replies(number_of_items=1)['items'][0]
    item2 = cc.get_saved_replies(number_of_items=1, offset=1)['items'][0]
    assert item1 != item2


def test_add_saved_reply(cc):
    response = cc.add_saved_reply('What colour is the sky?', 'Blue')
    assert 'replyId' in response
    assert 'answerId' in response


def test_delete_saved_reply(cc):
    reply_id = cc.delete_saved_reply(52)
    assert reply_id == '52'


def test_add_paraphrase_question(cc):
    question_id = cc.add_paraphrase_question(12, 'How old are you?')
    assert question_id is not None


def test_edit_paraphrase_question(cc):
    question_id = cc.edit_paraphrase_question(12, 'What is your age?')
    assert question_id == '12'


def test_edit_canonical_question(cc):
    reply_id = cc.edit_canonical_question(14, 'What age are you?')
    assert reply_id == '14'


def test_delete_paraphrase_question(cc):
    question_id = cc.delete_paraphrase_question(12)
    assert question_id == '12'


def test_add_answer(cc):
    answer_id = cc.add_answer(52, 'Grey')
    assert answer_id is not None


def test_edit_answer(cc):
    answer_id = cc.edit_answer(7, 'Gray')
    assert answer_id == '7'


def test_delete_answer(cc):
    answer_id = cc.delete_answer(7)
    assert answer_id == '7'
