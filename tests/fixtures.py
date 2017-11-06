import pytest
from cape.client import CapeClient


@pytest.fixture()
def cc():
    client = CapeClient()
    client.login('testuser', 'testpass')
    yield client
    client.logout()
