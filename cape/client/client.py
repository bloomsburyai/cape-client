import os.path
from requests import Session
from requests_toolbelt.multipart import encoder
from .exceptions import CapeException


API_VERSION = 0.1


class CapeClient:

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

    def get_user_token(self):
        """
        Retrieve a user token suitable for making 'answer' requests.

        :return: A user token
        """
        r = self._raw_api_call('get-user-token')
        return r.json()['result']['userToken']

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