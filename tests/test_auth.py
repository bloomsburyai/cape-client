import pytest
from cape.client import CapeClient
from cape.client import CapeException
from .fixtures import cc, API_URL, UNLUCKY_API_URL


def test_login():
    cc = CapeClient(API_URL)
    assert cc.logged_in() == False
    cc.login('blo', 'bla')
    assert cc.logged_in() == True


def test_logout():
    cc = CapeClient(API_URL)
    cc.login('blo', 'bla')
    assert cc.logged_in() == True
    cc.logout()
    assert cc.logged_in() == False


def test_failed_login():
    with pytest.raises(CapeException):
        cc = CapeClient(UNLUCKY_API_URL)
        cc.login('invalid', 'invalid')


def test_get_token(cc):
    token = cc.get_user_token()
    assert token is not None


def test_get_token_without_login():
    with pytest.raises(CapeException):
        cc = CapeClient(API_URL)
        cc.get_user_token()


def test_get_profile(cc):
    profile = cc.get_profile()
    assert len(profile) > 0


def test_get_admin_token(cc):
    admin_token = cc.get_admin_token()
    assert admin_token is not None


def test_set_forward_email(cc):
    email = cc.set_forward_email('test@bloomsbury.ai')
    assert email == 'test@bloomsbury.ai'
