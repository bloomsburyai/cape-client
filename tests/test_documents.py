import pytest, hashlib
from unittest.mock import Mock
from cape.client import CapeClient
from cape.client import CapeException
from .fixtures import cc, API_URL

document_text = "Welcome to the Cape API 0.1. Hopefully it's pretty easy to use."


def test_get_documents(cc):
    documents = cc.get_documents()
    assert 'totalItems' in documents
    assert 'items' in documents


def test_get_documents_number_of_items(cc):
    documents = cc.get_documents(number_of_items=1)
    assert len(documents['items']) == 1
    documents = cc.get_documents(number_of_items=2)
    assert len(documents['items']) == 2


def test_get_documents_ids(cc):
    documents = cc.get_documents(document_ids=["358e1b77c9bcc353946dfe107d6b32ff"])
    assert len(documents['items']) == 1


def test_text_upload(cc):
    document_id = cc.add_document("Cape API Documentation", document_text, origin='cape_api.txt')
    assert document_id == hashlib.sha256(document_text.encode('utf-8')).hexdigest()


def test_text_upload_without_login():
    with pytest.raises(CapeException):
        cc = CapeClient(API_URL)
        cc.add_document("Cape API Documentation", document_text, origin='cape_api.txt')


def test_file_upload(cc):
    fh = open("/tmp/cape_api.txt", "w")
    fh.write(document_text)
    fh.close()
    document_id = cc.add_document("Cape API Documentation", file_path="/tmp/cape_api.txt")
    assert document_id == hashlib.sha256(document_text.encode('utf-8')).hexdigest()


def test_file_upload_without_login():
    with pytest.raises(CapeException):
        cc = CapeClient(API_URL)
        fh = open("/tmp/cape_api.txt", "w")
        fh.write(document_text)
        fh.close()
        cc.add_document("Cape API Documentation", file_path="/tmp/cape_api.txt")


def test_large_upload(cc):
    fh = open("/tmp/large_cape_api.txt", "w")
    fh.write(document_text * 100000)
    fh.close()
    upload_cb = Mock()
    document_id = cc.add_document("Cape API Large Document", file_path="/tmp/large_cape_api.txt", monitor_callback=upload_cb)
    upload_cb.assert_called()
    assert document_id == hashlib.sha256((document_text * 100000).encode('utf-8')).hexdigest()


def test_text_and_file_hashes_match(cc):
    document_id1 = cc.add_document("Cape API Documentation", document_text, origin='cape_api.txt')
    fh = open("/tmp/cape_api.txt", "w")
    fh.write(document_text)
    fh.close()
    document_id2 = cc.add_document("Cape API Documentation", file_path="/tmp/cape_api.txt")
    assert document_id1 == document_id2


def test_delete_document(cc):
    document_id = cc.delete_document('document1')
    assert document_id == 'document1'
