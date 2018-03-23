import pytest
from cape.client import CapeClient


API_URL = 'https://ui-thermocline.thecape.ai/mock/full/api'
UNLUCKY_API_URL = 'https://ui-thermocline.thecape.ai/mock/unlucky/api'


@pytest.fixture()
def cc():
    client = CapeClient(API_URL)
    client.login('testuser', 'testpass')
    yield client
    client.logout()
