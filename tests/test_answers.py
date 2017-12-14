import pytest

from cape.client import CapeException
from .fixtures import cc


def test_answer(cc):
    answers = cc.answer("Is this API easy to use?")
    assert len(answers) == 1
    assert answers[0]['answerText'] is not None


def test_multiple_answers(cc):
    answers = cc.answer("Is this API easy to use?", number_of_items=2)
    assert len(answers) == 2


def test_document_ids(cc):
    answers = cc.answer("Is this API easy to use?", document_ids=["358e1b77c9bcc353946dfe107d6b32ff"])
    assert len(answers) == 1

def test_inline_answer(cc):
    answers = cc.answer("Is this API easy to use?", text="This API is easy to use.")
    assert len(answers) == 1

def test_answer_exceptions(cc):
    with pytest.raises(CapeException):
        cc.answer("")
    with pytest.raises(CapeException):
        cc.answer('')
    with pytest.raises(CapeException):
        cc.answer(' ')
    with pytest.raises(CapeException):
        cc.answer('?! "/')
