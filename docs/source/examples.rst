Examples
========

..  contents::
    :local:


Answering Questions
-------------------


Authentication
^^^^^^^^^^^^^^

Requests to the answer endpoint require a "user token", this enables developers to provide access to their Cape AI
by embedding their user token within their application.

The user token for your AI can either be retrieved through the `Cape UI <http://alpha.thecape.ai>`_ or through a call
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
            'text': "Hopefully it's pretty easy",
            'confidence': 0.75,
            'sourceType': 'document',
            'sourceId': '358e1b77c9bcc353946dfe107d6b32ff',
            'startOffset': 30,
            'endOffset': 56
        }
    ]

By default :meth:`cape.client.CapeClient.answer` will only fetch the answer with the highest confidence value, for
details on fetching multiple results see the :ref:`multiple answers <multiple-answers>` section.

Each answer in the list contains the following properties:

..  csv-table::
    :header: "Property", "Description"
    :delim: |

    text        |   The proposed answer to the question
    confidence  |   How confident the AI is that this is the correct answer
    sourceType  |   Whether this result came from a 'document'\, an 'faq' or 'notfound' if an answer wasn't found
    sourceId    |   The ID of the document or FAQ this answer was found in (depending on sourceType)
    startOffset |   The starting position of this answer in the document (if sourceType is 'document')
    endOffset   |   The end position of this answer in the document (if sourceType is 'document')


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
            'text': "Sam was born in 1974",
            'confidence': 0.74,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'startOffset': 20,
            'endOffset': 40
        },
        {
            'text': "James was born in 1982",
            'confidence': 0.73,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'startOffset': 120,
            'endOffset': 142
        },
        {
            'text': "Alice was born in 1973",
            'confidence': 0.71,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'startOffset': 255,
            'endOffset': 277
        },
        {
            'text': "Bob was born in 1965",
            'confidence': 0.71,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'startOffset': 310,
            'endOffset': 330
        },
        {
            'text': "Jill was born in 1986",
            'confidence': 0.70,
            'sourceType': 'document',
            'sourceId': 'employee_info.txt',
            'startOffset': 415,
            'endOffset': 436
        },
    ]

If we then wished to retrieve the next 5 answers we could run::

    answers = cc.answer('When were people born?',
                        USER_TOKEN,
                        number_of_items=5,
                        offset=5)

Which will return a further 5 answers starting with the 5th one. This allows us to retrieve answers in batches, only
fetching more when the user needs them.


Searching Specific Documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If we wish to search within a specific document (e.g. the document the user is currently viewing in our application) or
set of documents we can specify the *document_ids* when requesting an answer. For example::

    from cape.client import CapeClient

    USER_TOKEN = '08aerv08ajkdp'

    cc = CapeClient()
    answers = cc.answer('When was James born?',
                        USER_TOKEN,
                        document_ids = ['employee_info_2016.txt',
                                        'employee_info_2017.txt',
                                        'employee_info_2018.txt'])
    print(answers)

If we're explicitly searching through a document we may also wish to disable FAQ responses, this can be done with the
*documents_only* parameter::

    answers = cc.answer('When was James born?',
                        USER_TOKEN,
                        document_ids = ['employee_info_2016.txt',
                                        'employee_info_2017.txt',
                                        'employee_info_2018.txt'],
                        documents_only = True)


Managing Documents
------------------

Documents can be uploaded, updated and deleted using the client API. This functionality is only available to users with
administrative access and so requires them to login with the :meth:`cape.client.CapeClient.login` method.


Creating Documents
^^^^^^^^^^^^^^^^^^

There are two ways to create a new document, we can either provide the text contents of a document via the *text*
parameter of the :meth:`cape.client.CapeClient.upload_document` method or we can upload a file via the *file_path* parameter.

To create a document using the *text* parameter::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    doc_id = cc.upload_document("Document title",
                                "Hello and welcome to my document!")
    print(doc_id)

If we don't supply a *document_id* when calling :meth:`cape.client.CapeClient.upload_document` an ID will be
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
    doc_id = cc.upload_document("Document title",
                                file_path="/tmp/example_file.txt",
                                document_id='my_document_id')
    print(doc_id)

Because we supplied a *document_id* in this example the document ID we get returned will be what we requested:

    ``my_document_id``

As large file uploads may take a long time we may wish to provide the user with updates on the progress of our upload.
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
    doc_id = cc.upload_document("Document title",
                                file_path="/tmp/large_example.txt",
                                monitor_callback=upload_cb)
    print(doc_id)

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
    doc_id = cc.upload_document("My document",
                                "This is a good document.")

    # Replace it with an improved version
    cc.upload_document("My document",
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
control the size of the batches and retrieve multiple batches of documents, in a similar way to the mechanism described
in the :ref:`multiple answers <multiple-answers>` section. The response also includes the a *totalItems* property which
tells us the total number of items available (beyond those retrieved in this specific batch).

Each document in the list contains the following properties:

..  csv-table::
    :header: "Property", "Description"
    :delim: |

    id	358e1b77c9bcc353946dfe107d6b32ff	The ID of this document
title	API Documentation	The document's title (specified at upload)
origin	cape_api.txt	Where this document originally came from
text	Welcome to the Cape API 0.1. Hopefully it's pretty easy to use.	The contents of the document
created	1508161723	Timestamp of when this document was first uploaded


Managing Saved Replies
----------------------

Saved replies are made up of a pair consisting of a canonical question and the response it should produce. In addition
to the canonical question a saved reply may have many paraphrased questions associated with it which should produce the
same answer (e.g. "How old are you?" vs "What is your age?"). This functionality is only available to users with
administrative access and so requires them to login with the :meth:`cape.client.CapeClient.login` method.


Creating Saved Replies
^^^^^^^^^^^^^^^^^^^^^^

To create a new saved reply simply call the :meth:`cape.client.CapeClient.create_saved_reply` method with a question and
answer pair::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    reply_id = cc.create_saved_reply('What colour is the sky?', 'Blue')
    print(reply_id)

This will respond with the ID of the new reply:

    ``13``

Saved replies must have a unique question. If this question already exists then an error is returned.


Deleting Saved Replies
^^^^^^^^^^^^^^^^^^^^^^

To delete a saved reply simple pass its ID to the :meth:`cape.client.CapeClient.delete_saved_reply` method::

    from cape.client import CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    cc.delete_saved_reply(13)


Retrieving Saved Replies
^^^^^^^^^^^^^^^^^^^^^^^^

To retrieve a list of all saved replies use the :meth:`cape.client.CapeClient.get_saved_replies` method::

    from cape.client improt CapeClient

    cc = CapeClient()
    cc.login('username', 'password')
    replies = cc.get_saved_replies()
    print(replies)

This will return a list of replies::

    {
        'totalItems': 2,
        'items': [
            {
                'id': 322,
                'question': 'How old are you?',
                'answer': '18',
                'uses': 15,
                'created': 1508161734
            },
            {
                'id': 321,
                'question': 'What colour is the sky?',
                'answer': 'Blue',
                'uses': 1,
                'created': 1508161323
            }
        ]
    }

Each saved reply in the list contains the following properties:

..  csv-table::
    :header: "Property", "Description"
    :delim: |

    id          |   The reply ID
    question    |	The question to which the saved reply corresponds
    answer      |   The saved answer to respond with
    uses        |   How many times this saved reply is used to answer other questions (paraphrases)
    created     |   Timestamp indicating when this saved reply was created



Managing The Inbox
------------------

This functionality is only available to users with administrative access and so requires them to login with the
:meth:`cape.client.CapeClient.login` method.


Retrieving Inbox Items
^^^^^^^^^^^^^^^^^^^^^^


Marking Inbox Items As Read
^^^^^^^^^^^^^^^^^^^^^^^^^^^


Linking Inbox Items To Saved Replies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^