import pytest
from cape.client import CapeClient
from cape.client import CapeException
from .fixtures import cc


def test_annotations(cc):
    annotations = cc.get_annotations()
    assert 'totalItems' in annotations
    assert 'items' in annotations


def test_annotation_ids(cc):
    annotations = cc.get_annotations(annotation_ids=["e27b6285-c3c3-11e7-8d29-d15d28ee5381"])
    assert len(annotations['items']) == 1


def test_document_ids(cc):
    annotations = cc.get_annotations(document_ids=["f27b6283-c3c3-11e7-8d29-d15d28ee5381"])
    assert len(annotations['items']) == 1


def test_annotation_pages(cc):
    annotations = cc.get_annotations(pages=[1,2,3])
    assert len(annotations['items']) == 0
    annotations = cc.get_annotations(pages=[5])
    assert len(annotations['items']) == 30


def test_annotation_number_of_items(cc):
    annotations = cc.get_annotations(number_of_items=1)
    assert len(annotations['items']) == 1
    annotations = cc.get_annotations(number_of_items=2)
    assert len(annotations['items']) == 2


def test_annotation_offset(cc):
    item1 = cc.get_annotations(number_of_items=1)['items'][0]
    item2 = cc.get_annotations(number_of_items=1, offset=1)['items'][0]
    assert item1 != item2


def test_add_annotation(cc):
    response = cc.add_annotation('What colour is the sky?', 'Blue', document_id='sky', start_offset=4, end_offset=12)
    assert 'annotationId' in response
    assert 'answerId' in response


def test_add_annotation_metadata(cc):
    response = cc.add_annotation('What colour is the sky?', 'Blue', document_id='sky', start_offset=4, end_offset=12,
                                 metadata={
                                     'customfield': 'Test data'
                                 })
    assert 'annotationId' in response
    assert 'answerId' in response


def test_add_annotation_failure(cc):
    with pytest.raises(CapeException):
        response = cc.add_annotation('What am I missing?', 'Position parameters', document_id='sky')


def test_delete_annotation(cc):
    annotation_id = cc.delete_annotation("testid")
    assert annotation_id == 'testid'


def test_add_paraphrase_question(cc):
    question_id = cc.add_annotation_paraphrase_question('testid', 'How old are you?')
    assert question_id is not None


def test_edit_paraphrase_question(cc):
    question_id = cc.edit_annotation_paraphrase_question('testid', 'What is your age?')
    assert question_id == 'testid'


def test_edit_canonical_question(cc):
    annotation_id = cc.edit_annotation_canonical_question('testid', 'What age are you?')
    assert annotation_id == 'testid'


def test_delete_paraphrase_question(cc):
    question_id = cc.delete_annotation_paraphrase_question('testid')
    assert question_id == 'testid'


def test_add_answer(cc):
    answer_id = cc.add_annotation_answer('testid', 'Grey')
    assert answer_id is not None


def test_edit_answer(cc):
    answer_id = cc.edit_annotation_answer('testid', 'Gray')
    assert answer_id == 'testid'


def test_delete_answer(cc):
    answer_id = cc.delete_annotation_answer('testid')
    assert answer_id == 'testid'
