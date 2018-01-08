Examples
========

..  contents::
    :local:


.. _admin-authentication:

Admin Authentication
--------------------

There are two primary mechanisms for authentication within Cape: admin authentication, which provides full access to
your account and :ref:`user authentication <user-authentication>`, which only provides access to the answer endpoint.

There are two different ways to authenticate as an administrator, either through the
:meth:`cape.client.CapeClient.login` method::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')

Or you can authenticate using an admin token when creating the CapeClient object. This admin token can be
retrieved through the `Cape UI <http://ui.thecape.ai>`_::

    from cape.client import CapeClient

    cc = CapeClient(admin_token='youradmintoken')


Answering Questions
-------------------

.. _user-authentication:

Authentication
^^^^^^^^^^^^^^

Requests to the answer endpoint require a "user token", this enables developers to provide access to their Cape AI
by embedding their user token within their application.

The user token for your AI can either be retrieved through the `Cape UI <http://ui.thecape.ai>`_ or through a call
to the API::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    print(cc.get_user_token())

This will output a user token specific to your account, for example:

    ``08aerv08ajkdp``

Please note that while it is safe to distribute your user token as part of your application you should not include
your login credentials, as this provides full administration access to your account.


Answering A Question
^^^^^^^^^^^^^^^^^^^^

With the user token retrieved in the previous step we can now make calls to the answer endpoint. In its simplest
use-case this just requires us to pass the question and the user token to the :meth:`cape.client.CapeClient.answer`
method::

    from cape.client import CapeClient

    USER_TOKEN = '08aerv08ajkdp'

    cc = CapeClient()
    answers = cc.answer('How easy is this API to use?', USER_TOKEN)
    print(answers)

This will output the following answer list::

    [
        {
            'answerText': "Hopefully it's pretty easy",
            'answerContext: "Welcome to the Cape API 0.1. Hopefully it's pretty easy to use.",
            'confidence': 0.75,
            'sourceType': 'document',
            'sourceId': '358e1b77c9bcc353946dfe107d6b32ff',
            'answerTextStartOffset': 30,
            'answerTextEndOffset': 56,
            'answerContextStartOffset': 0,
            'answerContextEndOffset': 64
        }
    ]

By default :meth:`cape.client.CapeClient.answer` will only fetch the answer with the highest confidence value, for
details on fetching multiple results see the :ref:`multiple answers <multiple-answers>` section.

Each answer in the list contains the following properties:

..  _answer-objects:

..  csv-table::
    :header: "Property", "Description"
    :delim: |

    answerText                |   The proposed answer to the question
    answerContext             |   The context surrounding the proposed answer to the question
    confidence                |   How confident the AI is that this is the correct answer
    sourceType                |   Whether this result came from a 'document'\ or a 'saved_reply'
    sourceId                  |   The ID of the document or saved reply this answer was found in (depending on sourceType)
    answerTextStartOffset     |   The starting position of this answer in the document (if sourceType is 'document')
    answerTextEndOffset       |   The end position of this answer in the document (if sourceType is 'document')
    answerContextStartOffset  |   The starting position of this answer context in the document (if sourceType is 'document')
    answerContextEndOffset    |   The end position of this answer context in the document (if sourceType is 'document')


..  _multiple-answers:

Multiple Answers
^^^^^^^^^^^^^^^^

In some cases, such as when searching through a document or extracting information from multiple documents, it may be
desirable to retrieve more than one answer. This can be done via the *number_of_items* and *offset* parameters. For
example to retrieve the first 5 answers::

    from cape.client import CapeClient

    USER_TOKEN = '08aerv08ajkdp'

    cc = CapeClient()
    answers = cc.answer('When were people born?',
                        USER_TOKEN,
                        number_of_items=5)
    print(answers)

Which will produce output like::

    [
        {
            'answerText': "Sam was born in 1974",
            'answerContext: "did very good work. Sam was born in 1974 on the sunny island of",
            'confidence': 0.75,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'answerTextStartOffset': 80,
            'answerTextEndOffset': 100,
            'answerContextStartOffset':40,
            'answerContextEndOffset':123
        },
        {
            'answerText': "James was born in 1982",
            'answerContext: "James was born in 1982 on the sunny island of",
            'confidence': 0.64,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'answerTextStartOffset': 0,
            'answerTextEndOffset': 22,
            'answerContextStartOffset':0,
            'answerContextEndOffset':45
        },
        {
            'answerText': "Alice was born in 1973",
            'answerContext: "did very good work. Alice was born in 1973 on the sunny island of",
            'confidence': 0.61,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'answerTextStartOffset': 220,
            'answerTextEndOffset': 242,
            'answerContextStartOffset':200,
            'answerContextEndOffset':265
        },
        {
            'answerText': "Bob was born in 1965",
            'answerContext: "did very good work. Bob was born in 1965 on the sunny island of",
            'confidence': 0.59,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'answerTextStartOffset': 180,
            'answerTextEndOffset': 200,
            'answerContextStartOffset':140,
            'answerContextEndOffset':223
        },
        {
            'answerText': "Jill was born in 1986",
            'answerContext: "did very good work. Jill was born in 1986 on the sunny island of",
            'confidence': 0.57,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'answerTextStartOffset': 480,
            'answerTextEndOffset': 501,
            'answerContextStartOffset':440,
            'answerContextEndOffset':524
        }
    ]

If we then wished to retrieve the next 5 answers we could run::

    answers = cc.answer('When were people born?',
                        USER_TOKEN,
                        number_of_items=5,
                        offset=5)

Which will return a further 5 answers starting with the 6th one. This allows us to retrieve answers in batches, only
fetching more when the user needs them.


Searching Specific Documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If we wish to search within a specific document (e.g. the document the user is currently viewing in our application) or
in a set of documents we can specify the *document_ids* when requesting an answer. For example::

    from cape.client import CapeClient

    USER_TOKEN = '08aerv08ajkdp'

    cc = CapeClient()
    answers = cc.answer('When was James born?',
                        USER_TOKEN,
                        document_ids = ['employee_info_2016.txt',
                                        'employee_info_2017.txt',
                                        'employee_info_2018.txt'])
    print(answers)

If we're explicitly searching through a document we may also wish to disable saved reply responses, this can be done with the
*source_type* parameter::

    answers = cc.answer('When was James born?',
                        USER_TOKEN,
                        document_ids = ['employee_info_2016.txt',
                                        'employee_info_2017.txt',
                                        'employee_info_2018.txt'],
                        source_type = 'document')


Managing Documents
------------------

Documents can be uploaded, updated and deleted using the client API. This functionality is only available to users with
:ref:`administrative access <admin-authentication>`.


Creating Documents
^^^^^^^^^^^^^^^^^^

There are two ways to create a new document, we can either provide the text contents of a document via the *text*
parameter of the :meth:`cape.client.CapeClient.add_document` method or we can upload a file via the *file_path* parameter.

To create a document using the *text* parameter::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    doc_id = cc.add_document("Document title",
                                "Hello and welcome to my document!")
    print(doc_id)

If we don't supply a *document_id* when calling :meth:`cape.client.CapeClient.add_document` an ID will be
automatically generated for us. Automatically generated IDs are created by taking the SHA256 hash of the document
contents. So for this document the following ID will be produced:

    ``356477322741dbf8d8f0375ecdc6ae03357641829ae7ccf10283af36c5508a9d``

Alternatively we can upload a file::

    from cape.client import CapeClient

    # Create an example file
    fh = open('/tmp/example_file.txt', 'w')
    fh.write("Hello! This is an example file!")
    fh.close()

    cc = CapeClient()
    cc.login('username', 'password')
    doc_id = cc.add_document("Document title",
                                file_path="/tmp/example_file.txt",
                                document_id='my_document_id')
    print(doc_id)

Because we supplied a *document_id* in this example the document ID we get returned will be what we requested:

    ``my_document_id``

As large file uploads could take a long time we may wish to provide the user with updates on the progress of our upload.
To do this we can provide a callback function via the *monitor_callback* parameter which will provide us with frequent
updates about the upload's progress::

    from cape.client import CapeClient

    def upload_cb(monitor):
        print("%d/%d" % (monitor.bytes_read, monitor.len))

    # Create a large example file
    fh = open('/tmp/large_example.txt', 'w')
    fh.write("Hello! This is a large example file! " * 100000)
    fh.close()

    cc = CapeClient()
    cc.login('username', 'password')
    doc_id = cc.add_document("Document title",
                                file_path="/tmp/large_example.txt",
                                monitor_callback=upload_cb)

This will then print a series of status updates showing the progress of our file upload::

    ...
    2523136/3700494
    2531328/3700494
    2539520/3700494
    2547712/3700494
    2555904/3700494
    2564096/3700494
    2572288/3700494
    2580480/3700494
    ...


Updating Documents
^^^^^^^^^^^^^^^^^^

To update a document we simply upload a new document with the same *document_id* and set the *replace* parameter to
True. Without explicitly informing the server that we wish to replace the document it will report an error to avoid
accidental replacement of documents. For example::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')

    # Create the original document
    doc_id = cc.add_document("My document",
                             "This is a good document.")

    # Replace it with an improved version
    cc.add_document("My document",
                    "This is a great document.",
                    document_id=doc_id,
                    replace=True)


Deleting Documents
^^^^^^^^^^^^^^^^^^

To delete a document simply call the :meth:`cape.client.CapeClient.delete_document` method with the ID of the document
you wish to remove::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')

    cc.delete_document('my_bad_document')


Retrieving Documents
^^^^^^^^^^^^^^^^^^^^

The :meth:`cape.client.CapeClient.get_documents` method can be used to retrieve all previously uploaded documents::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')

    documents = cc.get_documents()
    print(documents)

This will output::

    {
        'totalItems': 2,
        'items': [
            {
                'id': 'custom_id_2',
                'title': 'document2.txt',
                'origin': 'document2.txt',
                'text': 'This is another document.',
                'created': 1508169352
            },
            {
               'id': '358e1b77c9bcc353946dfe107d6b32ff',
                'title': 'cape_api.txt',
                'origin': 'cape_api.txt',
                'text': "Welcome to the Cape API 0.1. " \
                        "Hopefully it's pretty easy to use.",
                'created': 1508161723
            }
        ]
    }

By default this will retrieve 30 documents at a time. The *number_of_items* and *offset* parameters can be used to
control the size of the batches and retrieve multiple batches of documents (similar to the mechanism described
in the :ref:`multiple answers <multiple-answers>` section). The response also includes the *totalItems* property which
tells us the total number of items available (beyond those retrieved in this specific batch).

Each document in the list contains the following properties:

..  csv-table::
    :header: "Property", "Description"
    :delim: |

    id          |	The ID of this document
    title       |	The document's title (specified at upload)
    origin	    |	Where this document originally came from
    text	    |   The contents of the document
    type        |   Whether this document was created by submitting text or from a file upload
    created	    |	Timestamp of when this document was first uploaded


Managing Saved Replies
----------------------

Saved replies are made up of a canonical question and the response it should produce. In addition
to the canonical question a saved reply may have many paraphrased questions associated with it which should produce the
same answer (e.g. "How old are you?" vs "What is your age?"). This functionality is only available to users with
:ref:`administrative access <admin-authentication>`.


Creating Saved Replies
^^^^^^^^^^^^^^^^^^^^^^

To create a new saved reply simply call the :meth:`cape.client.CapeClient.add_saved_reply` method with a question and
answer pair::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    reply_id = cc.add_saved_reply('What colour is the sky?', 'Blue')
    print(reply_id)

This will respond with a dictionary containing the ID of the new reply and the ID of the new answer::

    {
        'replyId': 'f9f1cf90-c3b1-11e7-91a1-9801a7ae6c69',
        'answerId': 'd2780710-c3c3-11e7-8d29-d15d28ee5381'
    }

Saved replies must have a unique question. If this question already exists then an error is returned.


Deleting Saved Replies
^^^^^^^^^^^^^^^^^^^^^^

To delete a saved reply pass its ID to the :meth:`cape.client.CapeClient.delete_saved_reply` method::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.delete_saved_reply("f9f1cf90-c3b1-11e7-91a1-9801a7ae6c69")


Retrieving Saved Replies
^^^^^^^^^^^^^^^^^^^^^^^^

To retrieve a list of all saved replies use the :meth:`cape.client.CapeClient.get_saved_replies` method::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    replies = cc.get_saved_replies()
    print(replies)

This will return a list of replies::

    {
        'totalItems': 2,
        'items': [
            {
                'id': 'd277e000-c3c3-11e7-8d29-d15d28ee5381',
                'canonicalQuestion': 'How old are you?',
                'answers': [
                    {
                        'id': 'd2780710-c3c3-11e7-8d29-d15d28ee5381',
                        'answer': '18'
                    }
                ],
                'paraphraseQuestions': [
                    {
                        'id': 'd2780711-c3c3-11e7-8d29-d15d28ee5381',
                        'question': 'What is your age?'
                    },
                    {
                        'id': 'd2780712-c3c3-11e7-8d29-d15d28ee5381',
                        'question': 'How many years old are you?'
                    }
                ],
                'created': 1508161734,
                'modified': 1508161734
            },
            {
                'id': 'd2780713-c3c3-11e7-8d29-d15d28ee5381',
                'canonicalQuestion': 'What colour is the sky?',
                'answers': [
                    {
                        'id': 'd2780714-c3c3-11e7-8d29-d15d28ee5381',
                        'answer': 'Blue'
                    }
                ],
                'paraphraseQuestions': [],
                'created': 1508161323,
                'modified': 1508161323
            }
        ]
    }

By default this will retrieve 30 saved replies at a time. The *number_of_items* and *offset* parameters can be used to
control the size of the batches and retrieve multiple batches of saved replies (similar to the mechanism
described in the :ref:`multiple answers <multiple-answers>` section). The response also includes the *totalItems*
property which tells us the total number of items available (beyond those retrieved in this specific batch).

Each saved reply in the list contains the following properties:

..  csv-table::
    :header: "Property", "Description"
    :delim: |

    id                  |   The reply ID
    canonicalQuestion   |   The question to which the saved reply corresponds
    answers             |	A list of saved answers, one of which will be selected at random as the response to the question.
    paraphraseQuestions	|	A list of questions which paraphase the canonical question
    modified	        |	Timestamp indicating when this saved reply was last modified
    created	            |	Timestamp indicating when this saved reply was created

It's also possible to search saved replies, for example to retrieve only saved replies containing the word 'blue'::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    replies = cc.get_saved_replies(search_term='blue')


Editing Saved Replies
^^^^^^^^^^^^^^^^^^^^^

There are three different parts of a saved reply that can be edited, the canonical question, the paraphrase questions
and the answers.


Adding Paraphrase Questions
"""""""""""""""""""""""""""

Paraphrase questions are alternative phrasings of the canonical question which should produce the same answer. For
example "What is your age?" can be considered a paraphrase of "How old are you?". These can be added with the
:meth:`cape.client.CapeClient.add_paraphrase_question` method::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    question_id = cc.add_paraphrase_question("f9f1cf90-c3b1-11e7-91a1-9801a7ae6c69", 'What is your age?')
    print(question_id)

This will respond with the ID of the newly created question:

    ``21e9689e-c3b2-11e7-8a22-9801a7ae6c69``


Editing Paraphrase Questions
""""""""""""""""""""""""""""

To edit a paraphrase question call :meth:`cape.client.CapeClient.edit_paraphrase_question` with the ID of the question
to edit and the new question text to modify it with::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.edit_paraphrase_question("21e9689e-c3b2-11e7-8a22-9801a7ae6c69", 'How many years old are you?')


Deleting Paraphrase Questions
"""""""""""""""""""""""""""""

To delete a paraphrase question simply call :meth:`cape.client.CapeClient.delete_paraphrase_question` with the ID of
question to be deleted::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.delete_paraphrase_question("21e9689e-c3b2-11e7-8a22-9801a7ae6c69")


Adding Answers
""""""""""""""

If multiple answers are added to a saved reply then one will be selected at random when responding. Additional answers
can be added with the :meth:`cape.client.CapeClient.add_answer` method::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    answer_id = cc.add_answer("68c445cc-c3b2-11e7-8a88-9801a7ae6c69", 'Grey')
    print(answer_id)

This will respond with the ID of the new answer:

    ``703acab4-c3b2-11e7-b8b1-9801a7ae6c69``


Deleting Answers
""""""""""""""""

To delete an answer call :meth:`cape.client.CapeClient.delete_answer` with the ID of the answer to be deleted::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.delete_answer("703acab4-c3b2-11e7-b8b1-9801a7ae6c69")

Because every saved reply must have at least one answer it's not possible to delete the last remaining answer in a saved
reply, in this case you may wish to consider deleting the saved reply itself.


Editing Canonical Questions
"""""""""""""""""""""""""""

To edit the canonical question call :meth:`cape.client.CapeClient.edit_canonical_question` with the ID of the saved
reply that it belongs to::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.edit_canonical_question("f9f1cf90-c3b1-11e7-91a1-9801a7ae6c69", 'What age are you?')


Managing The Inbox
------------------

The inbox provides a list of questions that have been asked by users and the response the system has replied with.
This functionality is only available to users with :ref:`administrative access <admin-authentication>`.

Retrieving Inbox Items
^^^^^^^^^^^^^^^^^^^^^^

To retrieve inbox items call the :meth:`cape.client.CapeClient.get_inbox` method::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    inbox = cc.get_inbox()
    print(inbox)

This returns a list of inbox items::

    {
        'totalItems': 2,
        'items': [
            {
                'id': '4124',
                'answered': False,
                'read': False,
                'question': 'Who are you?',
                'questionSource': 'API',
                'created': 1508162032,
                'answers': []
            },
            {
                'id': '4123',
                'answered': True,
                'read': False,
                'question': 'How easy is the API to use?',
                'questionSource': 'API',
                'created': 1508161834,
                'answers': [
                    {
                        'answerText': "Hopefully it's pretty easy",
                        'answerContext: "Welcome to the Cape API 0.1. Hopefully it's pretty easy to use.",
                        'confidence': 0.75,
                        'sourceType': 'document',
                        'sourceId': '358e1b77c9bcc353946dfe107d6b32ff',
                        'answerTextStartOffset': 30,
                        'answerTextEndOffset': 56,
                        'answerContextStartOffset': 0,
                        'answerContextEndOffset': 64
                    }
                ]
            }
        ]
    }

By default this will retrieve 30 inbox items at a time. The *number_of_items* and *offset* parameters can be used to
control the size of the batches and retrieve multiple batches of inbox items (similar to the mechanism
described in the :ref:`multiple answers <multiple-answers>` section). The response also includes the *totalItems*
property which tells us the total number of items available (beyond those retrieved in this specific batch).

Each inbox item in the list has the following properties:

..  csv-table::
    :header: "Property", "Description"
    :delim: |

    id          |	Unique ID for this inbox item
    question    |	The question that a user asked
    read        |	Whether this item has been read
    answered	|	Whether an answer could be found for this question
    answers     |   A list of :ref:`answer objects <answer-objects>`
    created     |   Timestamp indicating when this question was asked

Inbox items can be searched and filtered, for example to retrieve only inbox items that haven't been read but have been
answered and contain the word 'API'::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    inbox = cc.get_inbox(read=False, answered=True, search_term='api')


Marking Inbox Items As Read
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To mark an inbox item as having been read call the :meth:`cape.client.CapeClient.mark_inbox_read` method with the ID
of the inbox item to mark as having been read::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.mark_inbox_read('4123')


Archiving Inbox Items
^^^^^^^^^^^^^^^^^^^^^

Once an inbox item has been archived it will no longer appear in the list of inbox items returned by
:meth:`cape.client.CapeClient.get_inbox`. To archive an item call :meth:`cape.client.CapeClient.archive_inbox` with the
ID of the inbox item to archive::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.archive_inbox('4123')
