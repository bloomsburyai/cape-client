=================================================
How To Build A Simple AI-Powered Ctrl-F with Cape
=================================================

The Cape API is a an easy to use way to add advanced, AI-powered question answering to your application. In this
tutorial we show you how you can create an AI-Powered Ctrl-F using the Cape API with only a few lines of code.

You can view the finished demo here

..  contents::
    :local:


Getting Set Up
--------------

Requirements
^^^^^^^^^^^^

* Python 3.6+
* Python packages are defined within requirements.txt, you can install them with the following command::

    pip3 install -r requirements.txt

* A Cape Account. You can sign up with Google or Facebook, it's easy. `Do it now <https://alpha.thecape.ai>`_.

Getting The Code
^^^^^^^^^^^^^^^^

You can complete this tutorial in two ways. You can build up your code along the way, copying and pasting code snippets
where needed and adding boilerplate, or you can clone our `tutorial repository <https://github.com/bloogram/basic-ctrl-f-tutorials>`_ with
completed boilerplate code.

The default branch, ``begin`` has missing pieces of code that you'll be able to fill in during the tutorial. Another
branch, named ``completed`` has the completed code (minus authentication credentials) - so you should be able to use
it straight away!

What is  Cape API?
---------------------

.. _what_is_the_cape_api:

Cape API is an API that finds the bit of text in a document that answers a question. For examples, say you had a document
such as: ::

    "You should use the Cape API to build really cool question answering systems"

And you had a question like: ::

    "What could I use for building a qa system?"

Using our API, you'd be able to ask this question to the document and get out an answer like this: ::

    "Cape API"

Introduction To The Cape Client
-------------------------------

.. _cape_client_introduction:

We've written a Python client for Cape API that we'll be using to build our ctrl+f functionality.

Authenticating
^^^^^^^^^^^^^^

There are two ways to authenticate - with an **Admin Token** or your **username and password**.

**Note:** If you've created an account with Facebook or Google you won't have a password, so you'll have to use your admin token.
To get your amin token, login `here <https://alpha.thecape.ai>`_, go to the top right hand corner,
click on the cartoon head and shoulders and your admin token should be displayed.

Here's the code to authenticate with the **username and password**::

    from cape.client import CapeClient
    cape_client = CapeClient()
    # login with the client
    cape_client.login('USERNAME', 'PASSWORD')

Alternatively, you can use the **Admin Token**. ::

    from cape.client import CapeClient
    cape_client = CapeClient(admin_token=ADMIN_TOKEN)

The User Token And The Admin Token
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two types of token used in the Cape API: the **Admin Token** and the **User Token**.

The **Admin Token** gives you full control over your account, and is required for things like adding Documents, adding
Saved Replies etc. You can get your admin token from your online dashboard once logged in, and use it as a parameter
to your API calls even if you aren't logged in.::

    # set the default threshold to low - means the AI will
    # answer you more of the time, but will get more wrong
    cape_client.set_default_threshold('low')


The **User Token** is only used when answering questions. You can think of your User token as giving someone 'read'
access to your AI. The following code retrieves your user token so we can query our document for answers.::

    user_token = cape_client.get_user_token
    print(user_token)
    08aerv08ajkdp
Adding The Document You Want To Search
--------------------------------------

.. _adding_documents:

In our final demo we'll have a text area where you can copy and paste in a document you'd like to be able to search
and see the results immediately. To get started with this, we'll explore the upload documents functionality of the
Cape API.

The Upload Document Method
^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two ways to create a document - literally uploading a document from your filesystem (for the time being
restricted to markdown and txt documents), or passing a string as the body of the document in the add document method.
During this tutorial we'll be using the latter.

Let's say that someone has copied and pasted the following Wikipedia article on football into our text area::

    Football is a family of team sports that involve, to varying degrees, kicking a ball with the foot to score a goal.
    Unqualified, the word football is understood to refer to whichever form of football is the most popular in the
    regional context in which the word appears. Sports commonly called 'football' in certain places include:
    association football (known as soccer in some countries); gridiron football (specifically American football
    or Canadian football); Australian rules football; rugby football (either rugby league or rugby union); and Gaelic
    football.[1][2] These different variations of football are known as football codes.

    Various forms of football can be identified in history, often as popular peasant games. Contemporary codes of
    football can be traced back to the codification of these games at English public schools during the nineteenth
    century.[3][4] The expanse of the British Empire allowed these rules of football to spread to areas of British
    influence outside the directly controlled Empire.[5] By the end of the nineteenth century, distinct regional codes
    were already developing: Gaelic football, for example, deliberately incorporated the rules of local traditional
    football games in order to maintain their heritage.[6] In 1888, The Football League was founded in England,
    becoming the first of many professional football competitions. During the twentieth century, several of the
    various kinds of football grew to become some of the most popular team sports in the world.

Once we've got this string, we can add a Document to Cape using the Cape Client and start answering questions straight
away. ::

    doc_id = cape_client.upload_document("Football Document", WIKIPEDIA_TEXT)
    # you can ask a question to a specific document by referencing the document id
    answers = cc.answer('What is football?',
                        user_token,
                        document_ids = ['Football Document'],
                        source_type = 'document',
                        number_of_items=1)
    print(answers)
    # ['Football is a family of team sports']

Combining The Upload Document Method With Our Demo App
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For our demo app, we'll be taking the value of a textarea input and uploading that as our document. For the time being
we only have a python client, so let's create an endpoint that takes in the document and uploads it. Since this is a
demo, we'll use the `Flask <http://flask.pocoo.org/>`_ framework.

Let's say you have a textarea element like the following::

    <textarea class="form-control" id="documentText" rows="6"
        placeholder="copy and paste text here"></textarea>

With the following jquery snippet that will hit an `add_document` endpoint with the contents of the `documentText`
textarea::

    $(document).ready(function(){
        $('#documentText').bind('input propertychange', function () {
            $.post('/add_document', {'doc':$(this).val()});
        });
    });

We can then create an endpoint using a logged-in Cape Client::

    # create a _doc_id variable private to the source file, to be shared across endpoints
    _doc_it = ""

    # create add_document endpoint
    @app.route('/add_document', methods=['POST'])
    def add_document():
        doc_text = request.form.get('doc', "") # get the document text from the post request
        _doc_id = _cape_client.upload_document(title='ctrl_f_doc',
                                               text=doc_text,
                                               replace=True) # upload the document,
        print(f'uploaded doc with id: {_doc_id}')
        return jsonify({'success': True})

If you're using our boilerplate code, you can find the html for our demo in `templates/index.html`.

Adding The Search Functionality
-------------------------------





