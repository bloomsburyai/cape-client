import pytest
from cape.client import CapeClient
from cape.client import CapeException


def test_login():
    cc = CapeClient()
    assert cc.logged_in() == False
    cc.login('blo', 'bla')
    assert cc.logged_in() == True


def test_logout():
    cc = CapeClient()
    cc.login('blo', 'bla')
    assert cc.logged_in() == True
    cc.logout()
    assert cc.logged_in() == False


@pytest.mark.skip("Log in will always success against the mock API, so this is currently untestable")
def test_failed_login():
    with pytest.raises(CapeException):
        cc = CapeClient()
        cc.login('invalid', 'invalid')


def test_get_token():
    cc = CapeClient()
    cc.login('blo', 'bla')
    token = cc.get_user_token()
    assert token is not None


def test_get_token_without_login():
    with pytest.raises(CapeException):
        cc = CapeClient()
        cc.get_user_token()


def test_get_profile():
    cc = CapeClient()
    cc.login('blo', 'bla')
    profile = cc.get_profile()
    assert len(profile) > 0
