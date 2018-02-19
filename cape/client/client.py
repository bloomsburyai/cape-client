# Copyright (c) 2017 Blemundsbury AI Limited
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os.path
import json
from requests import Session
from requests_toolbelt.multipart import encoder
from .exceptions import CapeException
from .utils import check_list
import string

API_VERSION = 0.1


class CapeClient:
    """
        The CapeClient provides access to all methods of the Cape API.
    """

    def __init__(self, api_base='https://responder.thecape.ai/api', admin_token=None):
        """

        :param api_base: The URL to send API requests to.
        :param admin_token: An admin token to authenticate with.
        """
        self.api_base = "%s/%s" % (api_base, API_VERSION)
        self.session = Session()
        self.session_cookie = False
        self.admin_token = admin_token
        self.user_token = None

    def _raw_api_call(self, method, parameters=None, monitor_callback=None):
        if parameters is None:
            parameters={}
        url = "%s/%s" % (self.api_base, method)
        if 'token' in parameters:
            token = parameters.pop('token')
            url += "?token=%s" % token
        elif self.admin_token:
            url += "?adminToken=%s" % self.admin_token
        if 'documentIds' in parameters and not isinstance(parameters['documentIds'], str):
            parameters['documentIds'] = json.dumps(parameters['documentIds'])
        if parameters:
            m = encoder.MultipartEncoderMonitor.from_fields(fields=parameters, encoding='utf-8',
                                                            callback=monitor_callback)
            if self.session_cookie:
                r = self.session.post(url, data=m, cookies={'session': self.session_cookie},
                                      headers={'Content-Type': m.content_type})
            else:
                r = self.session.post(url, data=m, headers={'Content-Type': m.content_type})
        else:
            if self.session_cookie:
                r = self.session.get(url, cookies={'session': self.session_cookie})
            else:
                r = self.session.get(url)

        if r.status_code == 200 and r.json()['success']:
            return r
        else:
            raise CapeException(r.json()['result']['message'])

    def login(self, login, password):
        """
        Log in to the Cape API as an AI builder.

        :param login: The username to log in with.
        :param password: The password to log in with.
        :return:
        """
        r = self._raw_api_call('user/login', {'login': login, 'password': password})
        self.session_cookie = r.cookies['session']

    def logged_in(self):
        """
        Reports whether we're currently logged in.

        :return: Whether we're logged in or not.
        """
        return self.session_cookie != False or self.admin_token != None

    def logout(self):
        """
        Log out and clear the current session cookie.

        :return:
        """
        self._raw_api_call('user/logout')
        self.session_cookie = False
        self.user_token = None

    def get_admin_token(self):
        """
        Retrieve the admin token for the currently logged in user.

        :return: An admin token.
        """
        r = self._raw_api_call('user/get-admin-token')
        return r.json()['result']['adminToken']

    def get_user_token(self):
        """
        Retrieve a user token suitable for making 'answer' requests.

        :return: A user token.
        """
        r = self._raw_api_call('user/get-user-token')
        return r.json()['result']['userToken']

    def get_profile(self):
        """
        Retrieve the current user's profile.

        :return: A dictionary containing the user's profile.
        """
        r = self._raw_api_call('user/get-profile')
        return r.json()['result']

    def get_default_threshold(self):
        """
        Retrieve the default threshold used if one isn't explicitly specified when calling answer().

        :return: The current default threshold (either 'verylow', 'low', 'medium', 'high' or 'veryhigh').
        """
        r = self._raw_api_call('user/get-default-threshold')
        return r.json()['result']['threshold']

    def set_default_threshold(self, threshold):
        """
        Set the default threshold used if one isn't explicitly specified when calling answer().

        :param threshold: The new default threshold to set, must be either 'verylow', 'low', 'medium', 'high' or 'veryhigh'.
        :return: The new default threshold that's just been set.
        """
        r = self._raw_api_call('user/set-default-threshold', {'threshold': threshold})
        return r.json()['result']['threshold']

    def set_forward_email(self, email):
        """
        Set the email address that emails which couldn't be answered automatically are forwarded to.

        :param email: The new forward email address to set.
        :return: The new forward email address that's just been set.
        """
        r = self._raw_api_call('user/set-forward-email', {'email': email})
        return r.json()['result']['forwardEmail']

    def answer(self, question, user_token=None, threshold=None, document_ids=None,
               source_type='all', speed_or_accuracy='balanced', number_of_items=1, offset=0,
               text=None):
        """
        Provide a list of answers to a given question.

        :param question: The question to ask.
        :param user_token: A token retrieved from get_user_token (Default: the token for the currently authenticated user).
        :param threshold: The minimum confidence of answers to return ('verylow'/'low'/'medium'/'medium'/'veryhigh').
        :param document_ids: A list of documents to search for answers (Default: all documents).
        :param source_type: Whether to search documents, saved replies or all ('document'/'saved_reply'/'all').
        :param speed_or_accuracy: Prioritise speed or accuracy in answers ('speed'/'accuracy'/'balanced').
        :param number_of_items: The number of answers to return.
        :param offset: The starting point in the list of answers, used in conjunction with number_of_items to retrieve multiple batches of answers.
        :param text: An inline text to be treated as a document with id "Inline Text".
        :return: A list of answers.
        """
        document_ids = check_list(document_ids, 'document IDs')
        if not question.strip():
            raise CapeException('Expecting question parameter to not be empty string')
        invalidChars = set(string.punctuation.replace("_", ""))
        if all(ch in invalidChars for ch in question.strip().replace(" ", "")):
            raise CapeException(
                'All characters in question parameter are punctuation. At least one alpha-numeric character required.')
        params = {'token': user_token,
                  'question': question,
                  'threshold': threshold,
                  'documentIds': json.dumps(document_ids),
                  'sourceType': str(source_type),
                  'speedOrAccuracy': speed_or_accuracy,
                  'numberOfItems': str(number_of_items),
                  'offset': str(offset),
                  'text': text}
        if user_token is None:
            params.pop('token')
            if not self.logged_in():
                raise CapeException("A user token must be supplied if the client isn't logged in.")
        if len(document_ids) == 0:
            params.pop('documentIds')
        if threshold is None:
            params.pop('threshold')
        if text is None:
            params.pop('text')
        r = self._raw_api_call('answer', params)
        return r.json()['result']['items']

    def get_inbox(self, read='both', answered='both', search_term='', number_of_items=30, offset=0):
        """
        Retrieve the items in the current user's inbox.

        :param read: Filter messages based on whether they have been read.
        :param answered: Filter messages based on whether they have been answered.
        :param search_term: Filter messages based on whether they contain the search term.
        :param number_of_items:	The number of inbox items to return.
        :param offset: The starting point in the list of inbox items, used in conjunction with number_of_tems to retrieve multiple batches of inbox items.
        :return: A list of inbox items in reverse chronological order (newest first).
        """
        r = self._raw_api_call('inbox/get-inbox', {'read': str(read),
                                                   'answered': str(answered),
                                                   'searchTerm': search_term,
                                                   'numberOfItems': str(number_of_items),
                                                   'offset': str(offset)})
        return r.json()['result']

    def mark_inbox_read(self, inbox_id):
        """
        Mark an inbox item as having been read.

        :param inbox_id: The inbox item to mark as being read.
        :return: The ID of the inbox item that was marked as read.
        """
        r = self._raw_api_call('inbox/mark-inbox-read', {'inboxId': str(inbox_id)})
        return r.json()['result']['inboxId']

    def archive_inbox(self, inbox_id):
        """
        Archive an inbox item.

        :param inbox_id: The inbox item to archive.
        :return: The ID of the inbox item that was archived.
        """
        r = self._raw_api_call('inbox/archive-inbox', {'inboxId': str(inbox_id)})
        return r.json()['result']['inboxId']

    def get_saved_replies(self, search_term='', saved_reply_ids=None, number_of_items=30, offset=0):
        """
        Retrieve a list of saved replies.

        :param search_term: Filter saved replies based on whether they contain the search term.
        :param saved_reply_ids: List of saved reply IDs to return.
        :param number_of_items: The number of saved replies to return.
        :param offset: The starting point in the list of saved replies, used in conjunction with number_of_tems to retrieve multiple batches of saved replies.
        :return: A list of saved replies in reverse chronological order (newest first).
        """
        saved_reply_ids = check_list(saved_reply_ids, 'saved reply IDs')
        params = {'searchTerm': search_term,
                  'savedReplyIds': json.dumps(saved_reply_ids),
                  'numberOfItems': str(number_of_items),
                  'offset': str(offset)}
        if len(saved_reply_ids) == 0:
            params.pop('savedReplyIds')
        r = self._raw_api_call('saved-replies/get-saved-replies', params)

        return r.json()['result']

    def create_saved_reply(self, question, answer):
        return self.add_saved_reply(question, answer)

    def add_saved_reply(self, question, answer):
        """
        Create a new saved reply.

        Saved replies are made up of a pair consisting of a canonical question and the response it should produce.
        In addition to the canonical question a saved reply may have many paraphrased questions associated with it
        which should produce the same answer (e.g. "How old are you?" vs "What is your age?").

        :param question: The question this saved reply relates to.
        :param answer: The answer to reply with when the question is asked.
        :return: The IDs of the new saved reply and answer.
        """
        r = self._raw_api_call('saved-replies/add-saved-reply', {'question': question,
                                                                 'answer': answer})
        return r.json()['result']

    def delete_saved_reply(self, reply_id):
        """
        Delete a saved reply.

        :param reply_id: The ID of the saved reply to delete.
        :return: The ID of the saved reply that was deleted.
        """
        r = self._raw_api_call('saved-replies/delete-saved-reply', {'replyId': str(reply_id)})
        return r.json()['result']['replyId']

    def add_paraphrase_question(self, reply_id, question):
        """
        Add a new paraphrase question to an existing saved reply.

        :param reply_id: The ID of the saved reply to add this question to.
        :param question: The new paraphrase of this saved reply's canonical question.
        :return: The ID of the new question.
        """
        r = self._raw_api_call('saved-replies/add-paraphrase-question',
                               {'replyId': str(reply_id), 'question': question})
        return r.json()['result']['questionId']

    def edit_paraphrase_question(self, question_id, question):
        """
        Modify an existing paraphrase question.

        :param question_id: The ID of the question to modify.
        :param question: The modified question text.
        :return: The ID of the question that was modified.
        """
        r = self._raw_api_call('saved-replies/edit-paraphrase-question',
                               {'questionId': str(question_id), 'question': question})
        return r.json()['result']['questionId']

    def edit_canonical_question(self, reply_id, question):
        """
        Modify the canonical question belonging to a saved reply.

        :param reply_id: The ID of the saved reply to modify the canonical question of.
        :param question: The modified question text.
        :return: The ID of the saved reply that was modified.
        """
        r = self._raw_api_call('saved-replies/edit-canonical-question',
                               {'replyId': str(reply_id), 'question': question})
        return r.json()['result']['replyId']

    def delete_paraphrase_question(self, question_id):
        """
        Delete a paraphrase question.

        :param question_id: The ID of the paraphrase question to delete.
        :return: The ID of the paraphrase question that was deleted.
        """
        r = self._raw_api_call('saved-replies/delete-paraphrase-question', {'questionId': str(question_id)})
        return r.json()['result']['questionId']

    def add_answer(self, reply_id, answer):
        """
        Add a new answer to an existing saved reply.

        :param reply_id: The ID of the saved reply to add this answer to.
        :param answer: A new answer to add to the saved reply.
        :return: The ID of the newly created answer.
        """
        r = self._raw_api_call('saved-replies/add-answer', {'replyId': str(reply_id), 'answer': answer})
        return r.json()['result']['answerId']

    def edit_answer(self, answer_id, answer):
        """
        Modify an existing answer.

        :param answer_id: The ID of the answer to edit.
        :param answer: The modified answer text.
        :return: The ID of the answer that was modified.
        """
        r = self._raw_api_call('saved-replies/edit-answer', {'answerId': str(answer_id), 'answer': answer})
        return r.json()['result']['answerId']

    def delete_answer(self, answer_id):
        """
        Delete an existing an answer.

        :param answer_id: The ID of the answer to delete.
        :return: The ID of the answer that was deleted.
        """
        r = self._raw_api_call('saved-replies/delete-answer', {'answerId': str(answer_id)})
        return r.json()['result']['answerId']

    def get_documents(self, document_ids=None, number_of_items=30, offset=0):
        """
        Retrieve this user's documents.

        :param document_ids: A list of documents to return.
        :param number_of_items: The number of documents to return.
        :param offset: The starting point in the list of documents, used in conjunction with number_of_items to retrieve multiple batches of documents.
        :return: A list of documents in reverse chronological order (newest first).
        """
        document_ids = check_list(document_ids, 'document IDs')
        params = {'documentIds': json.dumps(document_ids),
                  'numberOfItems': str(number_of_items),
                  'offset': str(offset)}
        if len(document_ids) == 0:
            params.pop('documentIds')
        r = self._raw_api_call('documents/get-documents', params)
        return r.json()['result']

    def upload_document(self, title, text=None, file_path=None, document_id='', origin='', replace=False,
                        document_type=None, monitor_callback=None):
        return self.add_document(title, text, file_path, document_id, origin, replace, document_type, monitor_callback)

    def add_document(self, title, text=None, file_path=None, document_id='', origin='', replace=False,
                     document_type=None, monitor_callback=None):
        """
        Create a new document or replace an existing document.

        :param title: The title to give the new document.
        :param text: The plain text contents of the document (either text or file_path must be supplied).
        :param file_path: A file to upload (either text or file_path must be supplied).
        :param document_id: The ID to give the new document (Default: An SHA256 hash of the document contents).
        :param origin: Where the document came from.
        :param replace: If true and a document already exists with the same document ID it will be overwritten with the new upload. If false an error is returned when a document ID already exists.
        :param document_type: Whether this document was created by inputting text or uploading a file (if not set this will be automatically determined).
        :param monitor_callback: A method to call with updates on the file upload progress.
        :return: The ID of the uploaded document.
        """
        if text is not None:
            if document_type is None:
                document_type = 'text'
            r = self._raw_api_call('documents/add-document', {'title': title,
                                                              'text': text,
                                                              'documentId': document_id,
                                                              'origin': origin,
                                                              'replace': str(replace)},
                                   monitor_callback=monitor_callback)
        elif file_path is not None:
            if document_type is None:
                document_type = 'file'
            directory, file_name = os.path.split(file_path)
            fh = open(file_path, 'rb')
            r = self._raw_api_call('documents/add-document', {'title': title,
                                                              'text': fh,
                                                              'documentId': document_id,
                                                              'origin': origin,
                                                              'replace': str(replace)},
                                   monitor_callback=monitor_callback)
            fh.close()
        else:
            raise CapeException("Either the 'text' or the 'file_path' parameter are required for document uploads.")
        return r.json()['result']['documentId']

    def delete_document(self, document_id):
        """
        Delete a document.

        :param document_id: The ID of the document to delete.
        :return: The ID of the document that was deleted.
        """
        r = self._raw_api_call('documents/delete-document', {'documentId': document_id})
        return r.json()['result']['documentId']

    def add_annotation(self, question, answer, document_id, start_offset=None, end_offset=None, metadata=None):
        """
        Create a new annotation for a specified document.

        Annotations are made up of a pair consisting of a canonical question, the response it should produce and a
        location within a specific document that this answer corresponds to.

        In addition to the canonical question an annotation may have many paraphrased questions associated with it
        which should produce the same answer (e.g. "How old are you?" vs "What is your age?").

        :param question: The question this annotation relates to.
        :param answer: The answer to reply with when the question is asked.
        :param document_id: The document which this annotation corresponds to.
        :param start_offset: The starting location of the annotation within the specified document.
        :param end_offset: The ending location of the annotation within the specified document.
        :param metadata: A dictionary containing user definable metadata about this annotation.
        :return: The IDs of the new annotation and answer.
        """
        params = {
            'question': question,
            'answer': answer,
            'documentId': document_id,
            'startOffset': str(start_offset),
            'endOffset': str(end_offset),
            'metadata': json.dumps(metadata)
        }

        if start_offset is None:
            params.pop('startOffset')
        if end_offset is None:
            params.pop('endOffset')
        if metadata is None:
            params.pop('metadata')

        r = self._raw_api_call('annotations/add-annotation', params)

        return r.json()['result']

    def get_annotations(self, search_term='', annotation_ids=None, document_ids=None, pages=None, number_of_items=30,
                        offset=0):
        """
        Retrieve a list of annotations.

        :param search_term: Filter annotations based on whether they contain the search term.
        :param annotation_ids: A list of annotations to return/search within (Default: all annotations).
        :param document_ids: A list of documents to return annotations from (Default: all documents).
        :param pages: A list of pages to return annotations from (Default: all pages).
        :param number_of_items: The number of annotations to return.
        :param offset: The starting point in the list of annotations, used in conjunction with number_of_tems to retrieve multiple batches of annotations.
        :return: A list of annotations.
        """
        annotation_ids = check_list(annotation_ids, 'annotation IDs')
        document_ids = check_list(document_ids, 'document IDs')
        pages = check_list(pages, 'pages')

        params = {'searchTerm': search_term,
                  'annotationIds': json.dumps(annotation_ids),
                  'documentIds': json.dumps(document_ids),
                  'pages': json.dumps(pages),
                  'numberOfItems': str(number_of_items),
                  'offset': str(offset)}
        if len(annotation_ids) == 0:
            params.pop('annotationIds')
        if len(document_ids) == 0:
            params.pop('documentIds')
        if len(pages) == 0:
            params.pop('pages')
        r = self._raw_api_call('annotations/get-annotations', params)
        return r.json()['result']

    def delete_annotation(self, annotation_id):
        """
        Delete an annotation.

        :param annotation_id: The ID of the annotation to delete.
        :return: The ID of the annotation that was deleted.
        """
        r = self._raw_api_call('annotations/delete-annotation', {
            'annotationId': annotation_id
        })
        return r.json()['result']['annotationId']

    def edit_annotation_canonical_question(self, annotation_id, question):
        """
        Edit the canonical question of an annotation.

        :param annotation_id: The ID of the annotation to edit.
        :param question: The new canonical question for this annotation.
        :return: The ID of the annotation that was edited.
        """
        r = self._raw_api_call('annotations/edit-canonical-question', {
            'annotationId': annotation_id,
            'question': question
        })
        return r.json()['result']['annotationId']

    def add_annotation_paraphrase_question(self, annotation_id, question):
        """
        Add a new paraphrase question to an existing annotation.

        :param annotation_id: The ID of the annotation to add this question to.
        :param question: The new paraphrase of this annotation's canonical question.
        :return: The ID of the new question.
        """
        r = self._raw_api_call('annotations/add-paraphrase-question', {
            'annotationId': annotation_id,
            'question': question
        })
        return r.json()['result']['questionId']

    def edit_annotation_paraphrase_question(self, question_id, question):
        """
        Modify an existing paraphrase question in an annotation.

        :param question_id: The ID of the question to modify.
        :param question: The modified question text.
        :return: The ID of the question that was modified.
        """
        r = self._raw_api_call('annotations/edit-paraphrase-question', {
            'questionId': question_id,
            'question': question
        })
        return r.json()['result']['questionId']

    def delete_annotation_paraphrase_question(self, question_id):
        """
        Delete an annotation's paraphrase question.

        :param question_id: The ID of the question to delete.
        :return: The ID of the question that was deleted.
        """
        r = self._raw_api_call('annotations/delete-paraphrase-question', {
            'questionId': question_id
        })
        return r.json()['result']['questionId']

    def add_annotation_answer(self, annotation_id, answer):
        """
        Add a new answer to an existing annotation.

        :param annotation_id: The ID of the annotation to add this answer to.
        :param answer: The answer to add to the annotation.
        :return: The ID of the answer that was created.
        """
        r = self._raw_api_call('annotations/add-answer', {
            'annotationId': annotation_id,
            'answer': answer
        })
        return r.json()['result']['answerId']

    def edit_annotation_answer(self, answer_id, answer):
        """
        Edit an annotation's answer.

        :param answer_id: The ID of the answer to edit.
        :param answer: The new text to be used for this answer.
        :return: The ID of the answer that was edited.
        """
        r = self._raw_api_call('annotations/edit-answer', {
            'answerId': answer_id,
            'answer': answer
        })
        return r.json()['result']['answerId']

    def delete_annotation_answer(self, answer_id):
        """
        Delete an answer from an annotation.

        At least one answer must remain associated with an annotation.

        :param answer_id: The answer to delete
        :return: The ID of the answer that was deleted
        """
        r = self._raw_api_call('annotations/delete-answer', {
            'answerId': answer_id
        })
        return r.json()['result']['answerId']