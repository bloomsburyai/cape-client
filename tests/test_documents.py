import pytest, hashlib
from unittest.mock import Mock
from cape.client import CapeClient
from cape.client import CapeException

document_text = "Welcome to the Cape API 0.1. Hopefully it's pretty easy to use."

def test_text_upload():
    cc = CapeClient()
    cc.login('blo', 'bla')
    document_id = cc.upload_document("Cape API Documentation", document_text, origin='cape_api.txt')
    assert document_id == hashlib.sha256(document_text.encode('utf-8')).hexdigest()

def test_text_upload_without_login():
    with pytest.raises(CapeException):
        cc = CapeClient()
        cc.upload_document("Cape API Documentation", document_text, origin='cape_api.txt')
        
def test_file_upload():
    cc = CapeClient()
    cc.login('blo', 'bla')
    fh = open("/tmp/cape_api.txt", "w")
    fh.write(document_text)
    fh.close()
    document_id = cc.upload_document("Cape API Documentation", file_path="/tmp/cape_api.txt")
    assert document_id == hashlib.sha256(document_text.encode('utf-8')).hexdigest()

def test_file_upload_without_login():
    with pytest.raises(CapeException):
        cc = CapeClient()
        fh = open("/tmp/cape_api.txt", "w")
        fh.write(document_text)
        fh.close()
        cc.upload_document("Cape API Documentation", file_path="/tmp/cape_api.txt")

def test_large_upload():
    cc = CapeClient()
    cc.login('blo', 'bla')
    fh = open("/tmp/large_cape_api.txt", "w")
    fh.write(document_text * 100000)
    fh.close()
    upload_cb = Mock()
    document_id = cc.upload_document("Cape API Large Document", file_path="/tmp/large_cape_api.txt", monitor_callback=upload_cb)
    upload_cb.assert_called()
    assert document_id == hashlib.sha256((document_text * 100000).encode('utf-8')).hexdigest()

def test_text_and_file_hashes_match():
    cc = CapeClient()
    cc.login('blo', 'bla')
    document_id1 = cc.upload_document("Cape API Documentation", document_text, origin='cape_api.txt')
    fh = open("/tmp/cape_api.txt", "w")
    fh.write(document_text)
    fh.close()
    document_id2 = cc.upload_document("Cape API Documentation", file_path="/tmp/cape_api.txt")
    assert document_id1 == document_id2
