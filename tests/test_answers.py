import pytest
from cape.client import CapeClient
from cape.client import CapeException


def test_answer():
    cc = CapeClient()
    cc.login("blo", "bla")
    token = cc.get_user_token()
    answers = cc.answer(token, "Is this API easy to use?")
    assert answers[0]["text"] == "Hopefully it's pretty easy"

def test_multiple_answers():
    cc = CapeClient()
    cc.login("blo", "bla")
    token = cc.get_user_token()
    answers = cc.answer(token, "Is this API easy to use?", number_of_items=2)
    assert len(answers) == 2
