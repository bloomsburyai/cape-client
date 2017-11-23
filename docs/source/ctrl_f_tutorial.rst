=================================================
How To Build A Simple AI-Powered Ctrl-F with Cape
=================================================

..  contents::
    :local:

The Cape API is a an easy to use way to add advanced, AI-powered question answering to your application. In this
tutorial we show you how you can create an AI-Powered Ctrl-F using the Cape API with only a few lines of code.

Once finished, you'll have something that allows you to copy and paste in a piece of text and ask questions about it.
It'll look something like this:

.. image:: cape_ctrl_f.png


Getting Set Up
--------------

.. _getting_set_up:

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
branch, named ``master`` has the completed code (minus authentication credentials) - so you should be able to use
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

In our final tutorial we'll have a text area where you can copy and paste in a document you'd like to be able to search
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
    answers = cc.answer(query='What is football?',
                        token=user_token,
                        document_ids=['Football Document'],
                        source_type='document',
                        number_of_items=1)
    print(answers)
    # [{'text':'Football is a family of team sports',...},...]

Combining The Upload Document Method With Our App
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For our tutorial app, we'll be taking the value of a content editable input and uploading that as our document. For the time being
we only have a python client, so let's create an endpoint that takes in the document and uploads it. Since this is a
tutorial, we'll use the `Flask <http://flask.pocoo.org/>`_ framework.

Let's say you have a editable content element element like the following::

            <div class="form-control" id="documentText" contenteditable="True">Football is a family of team sports that
                involve, to varying degrees, kicking a ball with the foot to score a goal. Unqualified, the word
                football is understood to refer to whichever form of football is the most popular in the regional
                context in which the word appears. Sports commonly called 'football' in certain places include:
                association football (known as soccer in some countries); gridiron football (specifically American
                football or Canadian football); Australian rules football; rugby football (either rugby league or rugby
                union); and Gaelic football.[1][2] These different variations of football are known as football codes.
            </div>

With the following jquery snippet that will hit an `add_document` endpoint with the contents of the `documentText`
content editable::

    $(document).ready(function(){
        $('#documentText').bind('input propertychange', function () {
            $.post('/add_document', {'doc':$(this).val()});
        });
    });

We can then create an endpoint using a logged-in Cape Client::

    from flask import Flask, render_template, jsonify, request
    from cape.client import CapeClient

    _CAPE_CLIENT = CapeClient()
    _CAPE_CLIENT.login('USERNAME', 'PASSWORD')

    _LAST_DOC_ID = None
    _ANSWER_TOKEN = _CAPE_CLIENT.get_user_token() # to be used later
    _LAST_DOC_ID = None

    # create add_document endpoint
    @app.route('/add_document', methods=['POST'])
    def add_document():
        global _LAST_DOC_ID
        doc_text = request.form.get('doc', "") # get the document text from the post request
        _LAST_DOC_ID = _CAPE_CLIENT.upload_document(title='ctrl_f_doc',
                                                    text=doc_text,
                                                    replace=True) # upload the document,
        print(f'uploaded doc with id: {_LAST_DOC_ID}')
        return jsonify({'success': True})

If you're using our boilerplate code, you can find the html for our tutorial in `templates/index.html`.

Adding The Search Functionality
-------------------------------

.. _adding_search_functionality:

On to the exciting bit! Now we'll go over how we can add the search functionality to our website.

The Answer Method & Object
^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you've uploaded your documents, getting a response back is as simple as calling one method - :meth:cape.client.CapeClient.answer.
We've got an example below, which we'll discuss in more detail before jumping in to implementing the tutorial.::

    answers = cape_client.answer(query='What is football?',
                                 token=ANSWER_TOKEN,
                                 document_ids=[FOOTBALL_DOCUMENT_ID],
                                 source_type='document',
                                 number_of_items=5)
    print(answers)
    #  [{'text':'Football is a family of team sports',...}, ..., ... ]

Now let's go through each of these parameters in detail.

`query` is the string of the question you want answered.

`token` is your **Answer Token** (not your Admin Token!).

`document_ids` is an optional argument. It's a list of document IDs you want read when trying to find the answer to
your question. If you don't know, or don't care, which document your answer comes from you can set this to `None`.

`source_type` is another optional argument. We don't go into it here, but there are two ways you can answer questions
with Cape API - the first is by reading documents, but occassionally the right answer isn't found. Using something called
a **Saved Reply** you can manually override our reading AI. Since we aren't interested in this behaviour for this tutorial
we are going to explicitly set this parameter to `document` which means 'only get answers by reading documents'.

`number_of_items` is the number of answers you want returned. Our reading AI will try to find this number of answers in
the documents, and will return a sorted list of all those it thinks are good enough.

And what is returned? A list of 'Answers', where each answer is a python dictionary containing lots of useful information.
A sample Answer will look something like this::

    {
     'text': 'This is the answer text',
     'confidence': 0.88,
     'sourceType': 'document',
     'sourceId': '8dce9e4841fc944b120f7c5a31ea4dd73bfe41258206af37d5d43a2c74ab27c9',
     'startOffset': 0,
     'endOffset': 100
     }

Again, let's go through these attributes in turn to make sure we understand what's going on.

``text`` is the raw string that the AI thinks is the answer to your query.

``confidence`` is a float between 0 and 1 that represents how confident the AI is with this answer. This is primarily for
comparison purposes (i.e. you can compare different answers) - it shouldn't viewed as a probability (in the sense that
0.8 does not mean the model is right 8 times out of 10 when this confidence is present).

``sourceType`` tells you what type of object contained the answer. In this tutorial this key will always be 'document'.

``sourceId`` is the ID of the document that contained the answer.

``startOffset`` is the location in the document that corresponds to the first character of ``text``.

``endOffset`` is the location in the document that corresponds to the last character of ``text``.

Integrating The Answer Method Into Our Ctrl+F
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ok, so now we've introduction the answer method, let's integrate it into our tutorial. First, let's start with the html.
In our boilerplate code, we have the following input element::

    <input type="search" class="form-control mb-3" id="ctrlfField" placeholder="ctrl+f search bar"/>

For which we have the following jquery::

    $('#ctrlfField').bind('input propertychange', function (e) {
        e.preventDefault();
        if (typeof(myTimeout) !== "undefined") {
            clearTimeout(myTimeout);
        }
        myTimeout = setTimeout(function () {
            $.get('/ctrl_f', {'query': $('#ctrlfField').val()}, function (data) {
                var answers = data.answers;
                var answer = {};
                var range = [];
                for (i = 0; i < answers.length; i++) {
                    answer = answers[i];
                    range = {'start': answer.startOffset, 'length': (answer.endOffset - answer.startOffset)};
                    if (i === 0) {
                        $('#documentText').markRanges([range], {element: 'span', className: 'success'})
                    } else if (i < 4) {
                        $('#documentText').markRanges([range], {element: 'span', className: 'info'})
                    } else {
                        $('#documentText').markRanges([range], {element: 'span', className: 'danger'})
                    }
                }
            });
        }, 1000);
        return false;
    });

Since this isn't a jquery or javascript tutorial, I won't go into this code very much. The gist is that a get request
is sent to our 'ctrl_f' endpoint, and we leverage the excellent `mark.js <https://markjs.io/>`_ package to achieve the
highlighting effect.

I've added a few additional bits of logic to make the user experience better, but that complicate the code
a little. First, I've added a timeout to only send the request once the user has stopped typing for one second. Second,
I've assigned different classes to different answers based on index to indicate the answer the AI is more or less confident about.

Now let's get on to using the Python Cape Client. First we'll add the endpoint to our Flask server::

    @app.route('/ctrl_f', methods=['GET'])
    def ctrl_f():
        # DO CTRL-F LOGIC HERE
        pass

Our method inside the endpoint should do the following: (1) get the text from the search input field, (2) make a request
to the Cape API with this text and the document ID and (3) return the results of the request as a json object for our
javascript to highlight. The following code is an example of how we can get this done with the Cape Client::

    @app.route('/ctrl_f', methods=['GET'])
    def ctrl_f():
        if _LAST_DOC_ID is None:
            return jsonify({'success': False, 'answers': []}) # check that we've uploaded a document
        query_text = request.args['query'] # get the query text
        # get the answers from our answer endpoint, making sure to reference the correct document
        answers = _CAPE_CLIENT.answer(query_text,
                                      _ANSWER_TOKEN,
                                      document_ids=[_LAST_DOC_ID],
                                      number_of_items=5)
        print(f'answers: {answers}')
        return jsonify({'success': True,'answers': answers})

This is pretty much the full functionality required for our ctrl+f demo. Now we just need to put it all together.

Putting It All Together
-----------------------

.. _putting_it_all_together:

This is what our Python file looks like once we've added our index endpoint::

    from flask import Flask, render_template, jsonify, request
    from cape.client import CapeClient
    from settings import USERNAME, PASSWORD

    app = Flask(__name__)

    _CAPE_CLIENT = CapeClient()
    _CAPE_CLIENT.login(USERNAME, PASSWORD)

    _LAST_DOC_ID = None
    _ANSWER_TOKEN = _CAPE_CLIENT.get_user_token()


    @app.route('/')
    def index():
        return render_template('index.html')


    @app.route('/add_document', methods=['POST'])
    def add_document():
        global _LAST_DOC_ID
        doc_text = request.form.get('doc', "")
        _LAST_DOC_ID = _CAPE_CLIENT.upload_document(title='ctrl_f_doc', text=doc_text, replace=True)
        print(f'uploaded doc with id: {_LAST_DOC_ID}')
        return jsonify({'success': True})


    @app.route('/ctrl_f', methods=['GET'])
    def ctrl_f():
        if _LAST_DOC_ID is None:
            return jsonify({'success': False, 'answers': []})
        query_text = request.args['query']
        answers = _CAPE_CLIENT.answer(query_text,
                                      _ANSWER_TOKEN,
                                      document_ids=[_LAST_DOC_ID],
                                      number_of_items=5)
        print(f'answers: {answers}')
        return jsonify({'success': True,'answers': answers})


    if __name__ == '__main__':
        app.run(port='5050')

Our html file, `templates/index.html` is also very basic::

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css"
              integrity="sha384-PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb" crossorigin="anonymous">
        <link rel="stylesheet" href="/static/style.css">
        <meta charset="UTF-8">
        <title>Basic AI Powered Ctrl+F Demo</title>
    </head>
    <body>
    <div class="container">
        <div class="col">
            <h1 class="display-1">Cape Ctrl+F Demo</h1>
            <p class="text-muted lead">This super-powered ctrl+f demo was built using Cape API. View the tutorial <a
                    href="#">here.</a></p>
            <div class="form-group">
                <input type="search" class="form-control mb-3" id="ctrlfField" placeholder="ctrl+f search bar"/>
                <div class="form-control" id="documentText" contenteditable="True">Football is a family of team sports that
                    involve, to varying degrees, kicking a ball with the foot to score a goal. Unqualified, the word
                    football is understood to refer to whichever form of football is the most popular in the regional
                    context in which the word appears. Sports commonly called 'football' in certain places include:
                    association football (known as soccer in some countries); gridiron football (specifically American
                    football or Canadian football); Australian rules football; rugby football (either rugby league or rugby
                    union); and Gaelic football.[1][2] These different variations of football are known as football codes.
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.2.1.min.js"
            integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
            crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.3/umd/popper.min.js"
            integrity="sha384-vFJXuSJphROIrBnz7yo7oB41mKfc8JzQZiCq4NCceLEaO4IHwicKwpJf9c9IpFgh"
            crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js"
            integrity="sha384-alpBpkh1PFOepccYVYDB4do5UnbKysX5WZXm3XxPqe5iKTfUKjNkCk9SaVuEZflJ"
            crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.0/jquery.mark.es6.min.js"></script>
    <script src="/static/app.js"></script>
    </body>
    </html>

Our javascript is only a few lines long::

    $(document).ready(function () {
    var myTimeout = null;
    $('#documentText').bind('input propertychange', function () {
        $.post('/add_document', {'doc': $(this).text()});
    });
    $('#ctrlfField').bind('input propertychange', function (e) {
        e.preventDefault();
        if (typeof(myTimeout) !== "undefined") {
            clearTimeout(myTimeout);
        }
        myTimeout = setTimeout(function () {
            $.get('/ctrl_f', {'query': $('#ctrlfField').val()}, function (data) {
                var answers = data.answers;
                var answer = {};
                var range = [];
                for (i = 0; i < answers.length; i++) {
                    answer = answers[i];
                    range = {'start': answer.startOffset, 'length': (answer.endOffset - answer.startOffset)};
                    if (i === 0) {
                        $('#documentText').markRanges([range], {element: 'span', className: 'success'})
                    } else if (i < 4) {
                        $('#documentText').markRanges([range], {element: 'span', className: 'info'})
                    } else {
                        $('#documentText').markRanges([range], {element: 'span', className: 'danger'})
                    }
                }
            });
        }, 1000);
        return false;
    });
    });

And our stylesheet even shorter::

    .success {
    background: rgba(23, 162, 184, 0.5);
    }

    .info {
        background: rgba(23, 162, 184, 0.2);
    }

    .danger {
        background: rgba(23, 162, 184, 0.1);
    }

We can now run the whole thing by typing ``python3 app.py`` in the root of the directory and you are done!















