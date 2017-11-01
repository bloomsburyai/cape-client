import os.path
from requests import Session
from requests_toolbelt.multipart import encoder
from .exceptions import CapeException


API_VERSION = 0.1


class CapeClient:
    """
        The CapeClient provides access to all methods of the Cape API.
    """

    def __init__(self, api_base='https://ui.thecape.ai/mock/full/api'):
        """

        :param api_base: The URL to send API requests to.
        """
        self.api_base = "%s/%s" % (api_base, API_VERSION)
        self.session = Session()
        self.session_cookie = False

    def _raw_api_call(self, method, parameters={}, monitor_callback=None):
        url = "%s/%s" % (self.api_base, method)
        if parameters != {}:
            m = encoder.MultipartEncoderMonitor.from_fields(fields=parameters, encoding='utf-8', callback=monitor_callback)
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

        :param login: The username to log in with
        :param password: The password to log in with
        :return:
        """
        r = self._raw_api_call('login', {'login' : login, 'password' : password})
        self.session_cookie = r.cookies['session']

    def logged_in(self):
        """
        Reports whether we're currently logged in.

        :return: Whether we're logged in or not
        """
        return self.session_cookie != False

    def logout(self):
        """
        Log out and clear the current session cookie.

        :return:
        """
        self._raw_api_call('logout')
        self.session_cookie = False

    def get_admin_token(self):
        """
        Retrieve the admin token for the currently logged in user.

        :return: An admin token
        """
        r = self._raw_api_call('get-admin-token')
        return r.json()['result']['adminToken']

    def get_user_token(self):
        """
        Retrieve a user token suitable for making 'answer' requests.

        :return: A user token
        """
        r = self._raw_api_call('get-user-token')
        return r.json()['result']['userToken']

    def get_profile(self):
        """
        Retrieve the current user's profile

        :return: A dictionary containing the user's profile
        """
        r = self._raw_api_call('get-profile')
        return r.json()['result']

    def answer(self, question, token, threshold='high', document_ids=[], documents_only=False, speed_or_accuracy='balanced', number_of_items=1, offset=0):
        """
        Provide a list of answers to a given question.

        :param question: The question to ask
        :param token: A token retrieved from get_user_token
        :param threshold: The minimum confidence of answers to return ('high'/'medium'/'low')
        :param document_ids: A list of documents to search for answers (Default: all documents)
        :param documents_only: If true only answers from documents are returned without FAQ results
        :param speed_or_accuracy: Prioritise speed or accuracy in answers ('speed'/'accuracy'/'balanced')
        :param number_of_items: The number of answers to return
        :param offset: The starting point in the list of answers, used in conjunction with number_of_items to retrieve multiple batches of answers.
        :return: A list of answers
        """
        params = {'token': token,
                  'question': question,
                  'threshold': threshold,
                  'documentIds': str(document_ids),
                  'documentsOnly': str(documents_only),
                  'speedOrAccuracy': speed_or_accuracy,
                  'numberOfItems': str(number_of_items),
                  'offset': str(offset)}
        if len(document_ids) == 0:
            params.pop('documentIds')
        r = self._raw_api_call('answer', params)
        return r.json()['result']['items']

    def get_inbox(self, read='both', answered='both', search_term='', number_of_items=30, offset=0):
        """
        Retrieve the items in the current user's inbox.

        :param read: Filter messages based on whether they have been read
        :param answered: Filter messages based on whether they have been answered
        :param search_term: Filter messages based on whether they contain the search term
        :param number_of_items:	The number of inbox items to return
        :param offset: The starting point in the list of inbox items, used in conjunction with number_of_tems to retrieve multiple batches of inbox items.
        :return: A list of inbox items in reverse chronological order (newest first)
        """
        r = self._raw_api_call('get-inbox', {'read': str(read),
                                             'answered': str(answered),
                                             'searchTerm': search_term,
                                             'numberOfItems': str(number_of_items),
                                             'offset': str(offset)})
        return r.json()['result']

    def mark_inbox_read(self, inbox_id):
        """
        Mark an inbox item as having been read.

        :param inbox_id: The inbox item to mark as being read
        :return: The ID of the inbox item that was marked as read
        """
        r = self._raw_api_call('mark-inbox-read', {'inboxId': str(inbox_id)})
        return r.json()['result']['inboxId']

    def link_inbox_to_reply(self, inbox_id, reply_id):
        """
        When an inbox item is linked to a saved reply it is automatically marked as being answered.

        :param inbox_id: The inbox item to link
        :param reply_id: The saved reply to link it to
        :return: The ID of the inbox item and the reply it was linked to
        """
        r = self._raw_api_call('link-inbox-to-reply', {'inboxId': str(inbox_id),
                                                       'replyId': str(reply_id)})
        return r.json()['result']

    def unlink_inbox_from_reply(self, inbox_id):
        """
        When an inbox item is unlinked from a saved reply it is automatically returned to being unanswered.

        :param inbox_id: The inbox item to unlink
        :return: The ID of the inbox item that was unlinked
        """
        r = self._raw_api_call('unlink-inbox-from-reply', {'inboxId': str(inbox_id)})
        return r.json()['result']['inboxId']

    def get_saved_replies(self, search_term='', number_of_items=30, offset=0):
        """
        Retrieve a list of saved replies.

        :param search_term: Filter saved replies based on whether they contain the search term
        :param number_of_items: The number of saved replies to return
        :param offset: The starting point in the list of saved replies, used in conjunction with number_of_tems to retrieve multiple batches of saved replies.
        :return: A list of saved replies in reverse chronological order (newest first)
        """
        r = self._raw_api_call('get-saved-replies', {'searchTerm': search_term,
                                                     'numberOfItems': str(number_of_items),
                                                     'offset': str(offset)})
        return r.json()['result']

    def create_saved_reply(self, question, answer):
        """
        Create a new saved reply.

        Saved replies are made up of a pair consisting of a canonical question and the response it should produce.
        In addition to the canonical question a saved reply may have many paraphrased questions associated with it
        which should produce the same answer (e.g. "How old are you?" vs "What is your age?").

        :param question: The question this saved reply relates to
        :param answer: The answer to reply with when the question is asked
        :return: The ID of the new saved reply
        """
        r = self._raw_api_call('create-saved-reply', {'question': question,
                                                      'answer': answer})
        return r.json()['result']['replyId']

    def delete_saved_reply(self, reply_id):
        """
        Delete a saved reply.

        :param reply_id: The ID of the saved reply to delete
        :return: The ID of the saved reply that was deleted
        """
        r = self._raw_api_call('delete-saved-reply', {'replyId': str(reply_id)})
        return r.json()['result']['replyId']

    def get_documents(self, document_ids=[], number_of_items=30, offset=0):
        """
        Retrieve this user's documents.

        :param document_ids: A list of documents to return
        :param number_of_items: The number of documents to return
        :param offset: The starting point in the list of documents, used in conjunction with number_of_items to retrieve multiple batches of documents
        :return: A list of documents in reverse chronological order (newest first)
        """
        params = {'documentIds': document_ids,
                  'numberOfItems': str(number_of_items),
                  'offset': str(offset)}
        if len(document_ids) == 0:
            params.pop('documentIds')
        r = self._raw_api_call('get-documents', params)
        return r.json()['result']

    def upload_document(self, title, text=None, file_path=None, document_id='', origin='', replace=False,
                        monitor_callback=None):
        """
        Create a new document or replace an existing document.

        :param title: The title to give the new document
        :param text: The plain text contents of the document (either text or file_path must be supplied)
        :param file_path: A file to upload (either text or file_path must be supplied)
        :param document_id: The ID to give the new document (Default: An SHA256 hash of the document contents)
        :param origin: Where the document came from
        :param replace: If true and a document already exists with the same document ID it will be overwritten with the new upload. If false an error is returned when a documentId already exists.
        :param monitor_callback:
        :return: The ID of the uploaded document
        """
        if text is not None:
            r = self._raw_api_call('upload-document', {'title': title,
                                                       'text': text,
                                                       'documentId': document_id,
                                                       'origin': origin,
                                                       'replace': str(replace)}, monitor_callback=monitor_callback)
        elif file_path is not None:
            directory, file_name = os.path.split(file_path)
            fh = open(file_path, 'rb')
            r = self._raw_api_call('upload-document', {'title': title,
                                                       'text': fh,
                                                       'documentId': document_id,
                                                       'origin': origin,
                                                       'replace': str(replace)}, monitor_callback=monitor_callback)
            fh.close()
        else:
            raise CapeException("Either the 'text' or the 'file_path' parameter are required for document uploads.")
        return r.json()['result']['documentId']

    def delete_document(self, document_id):
        """

        :param document_id: The ID of the document to delete
        :return: The ID of the document that was deleted
        """
        r = self._raw_api_call('delete-document', {'documentId': document_id})
        return r.json()['result']['documentId']

    def get_default_message(self):
        """
        Retrieve the message used when the system isn't able to find an answer above the requested threshold.

        :return: The message currently used when an answer couldn't be found.
        """
        r = self._raw_api_call('get-default-message')
        return r.json()['result']['message']

    def set_default_message(self, message):
        """
        Set the message used when the system isn't able to find an answer above the requested threshold.

        :param message: The new default message to set.
        :return: The new default message that's just been set
        """
        r = self._raw_api_call('set-default-message', {'message': message})
        return r.json()['result']['message']

    def get_default_threshold(self):
        """
        Retrieve the default threshold used if one isn't explicitly specified when calling answer()

        :return: The current default threshold (either 'low', 'medium' or 'high')
        """
        r = self._raw_api_call('get-default-threshold')
        return r.json()['result']['threshold']

    def set_default_threshold(self, threshold):
        """
        Set the default threshold used if one isn't explicitly specified when calling answer()

        :param threshold: The new default threshold to set, must be either 'low', 'medium' or 'high'
        :return: The new default threshold that's just been set
        """
        r = self._raw_api_call('set-default-threshold', {'threshold': threshold})
        return r.json()['result']['threshold']
