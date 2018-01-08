=================================================
How To Build A Simple AI-Powered Ctrl-F with Cape
=================================================

..  contents::
    :local:

The Cape API is a an easy to use way to add advanced, AI-powered question answering to your application. In this
tutorial we show you how you can create an AI-Powered Ctrl-F using the Cape API with only a few lines of code.

Once finished, you'll have something that allows you to copy and paste in a piece of text and ask questions about it.


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

The default branch, ``master`` is the completed code — once you've installed the Python requirements in ``requirements.txt``
 you should be able to type the command ``python app.py`` in the root directory and play with the finished tutorial already.

There is another branch, ``begin``, which has removed parts of the Python and JavaScript code. Starting with this branch,
 you should be able to copy and paste in parts as we go along and end up with the finished product :).

Introduction To The Cape Client
-------------------------------

.. _cape_client_introduction:

We've written a Python client for Cape API that we'll be using to build our Ctrl+F functionality. Before we get started building, let’s go through some of the basic stuff
 - Authentication and Tokens.

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

    my_user_token = cape_client.get_user_token()
    print(my_user_token) # 08aerv08ajkdp

Adding The Document You Want To Search
--------------------------------------

.. _adding_documents:

In our final demo we have area where you can copy and paste in a document you'd like to be able to search
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

    # WIKIPEDIA_TEXT is the string of the doc you want to upload
    doc_id = cape_client.upload_document("Football Document", WIKIPEDIA_TEXT)
    # you can ask a question to a specific document by referencing the document id
    answers = cc.answer(question='What is football?',
                        user_token=my_user_token,
                        document_ids=[doc_id],
                        source_type='document',
                        number_of_items=1)
    print(answers) # [{'answerText':'Football is a family of team sports',...},...]

Adding The Upload Document Method Into Our App
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For our tutorial app, we'll be taking the value of a content editable input and uploading that as our document. For the time being
we only have a Python client, so let's create an endpoint that takes in the document and uploads it. Since this is a
tutorial, we'll use the `Flask <http://flask.pocoo.org/>`_ framework.

In our tutorial we have an editable content HTML element that contains text about Football in ``templates/index.html``::

            <div class="form-control" id="documentText" contenteditable="True">Football is a family of team sports that
                involve, to varying degrees, kicking a ball with the foot to score a goal. Unqualified, the word
                football is understood to refer to whichever form of football is the most popular in the regional
                context in which the word appears. Sports commonly called 'football' in certain places include:
                association football (known as soccer in some countries); gridiron football (specifically American
                football or Canadian football); Australian rules football; rugby football (either rugby league or rugby
                union); and Gaelic football.[1][2] These different variations of football are known as football codes.
            </div>

And we’ve already written the following jQuery snippet that will hit an ‘add_document’ endpoint with a post request
 with the contents of the element. You can add this to ``static/app.js``::

    $(document).ready(function(){
        $('#documentText').bind('input propertychange', function () {
            $.post('/add_document', {'doc':$(this).val()});
        });
    });

We can then create an endpoint using a logged-in Cape Client. The file you want to edit here is app.py in the root directory::

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


Adding The Search Functionality
-------------------------------

.. _adding_search_functionality:

On to the exciting bit! Now we'll go over how we can add the search functionality to our website.

The Answer Method & Object
^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you've uploaded your documents, getting a response back is as simple as calling one method - :meth:`cape.client.CapeClient.answer`
which returns a ranked list of answers. We've got an example below, which we'll discuss in more detail before jumping in to implementing the tutorial.::

    answers = cape_client.answer(question='What is football?',
                                 user_token=ANSWER_TOKEN,
                                 document_ids=[FOOTBALL_DOCUMENT_ID],
                                 source_type='document',
                                 number_of_items=5)
    print(answers)
    #  [{'answerText':'Football is a family of team sports',...}, ..., ... ]

Now let's go through each of these parameters in detail.

`query` is the string of the question you want answered.

`token` is your **User Token** (not your Admin Token!).

`document_ids` is an optional argument. It's a list of document IDs you want read when trying to find the answer to
your question. If you don't know, or don't care, which document your answer comes from you can set this to `None`.

`source_type` is another optional argument. We don't go into it here, but there are two ways you can answer questions
with Cape API - the first is by reading documents, but occasionally the right answer isn't found. Using something called
a **Saved Reply** you can manually override our reading AI. Since we aren't interested in this behaviour for this tutorial
we are going to explicitly set this parameter to `document` which means 'only get answers by reading documents'.

`number_of_items` is the number of answers you want returned. Our reading AI will try to find this number of answers in
the documents, and will return a sorted list of all those it thinks are good enough.

And what is an **Answer** object? Each **Answer** is a Python dictionary containing lots of useful information.
A sample Answer will look something like this::

    {
         'answerText': 'This is the answer text',
         'answerContext': 'context for This is the answer text',
         'confidence': 0.88,
         'sourceType': 'document',
         'sourceId': '8dce9e4841fc944b120f7c5a31ea4dd73bfe41258206af37d5d43a2c74ab27c9',
         'answerTextStartOffset': 10,
         'answerTextEndOffset': 100,
         'answerContextStartOffset': 0,
         'answerContextEndOffset': 120,
    }

Again, let's go through these attributes in turn to make sure we understand what's going on.

``answerText`` is the raw string that the AI thinks is the answer to your query.

``confidence`` is a float between 0 and 1 that represents how confident the AI is with this answer.

``sourceType`` tells you what type of object contained the answer. In this tutorial the ``sourceType`` key will always be 'document'.

``sourceId`` is the ID of the document that contained the answer.

``answerTextStartOffset`` is the location in the document that corresponds to the first character of ``answerText``.

``answerTextEndOffset`` is the location in the document that corresponds to the last character of ``answerText``.

``answerContextStartOffset`` is the location in the document that corresponds to the first character of ``answerContext``.

``answerContextEndOffset`` is the location in the document that corresponds to the last character of ``answerContext``.

Integrating The Answer Method Into Our Ctrl+F
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ok, so now we've introduction the answer method, let's integrate it into our tutorial. First, let's start with the html.
In our boilerplate code, we have the following input element::

    <input type="search" class="form-control mb-3" id="ctrlfField" placeholder="ctrl+f search bar"/>

For which we have the following jQuery::

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
                    range = {'start': answer.startTextOffset, 'length': (answer.endTextOffset - answer.startTextOffset)};
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

Since this isn't a jQuery or JavaScript tutorial, I won't go into this code very much. The gist is that a get request
is sent to our 'ctrl_f' endpoint, and we leverage the excellent `mark.js <https://markjs.io/>`_ package to achieve the
highlighting effect.

I've added a few additional bits of logic to make the user experience better, but that complicate the code
a little. First, I've added a timeout to only send the request once the user has stopped typing for one second.Second,
I’ve assigned difference classes to different answers based on the order to indicate how confident the AI is about
an answer.

Now let's get on to using the Python Cape Client. First we'll add the endpoint to our Flask server::

    @app.route('/ctrl_f', methods=['GET'])
    def ctrl_f():
        # DO CTRL-F LOGIC HERE
        pass

Our method inside the endpoint should do the following: (1) get the text from the search input field, (2) make a request
to the Cape API with this text and the document ID and (3) return the results of the request as a json object for our
JavaScript to highlight. The following code is an example of how we can get this done with the Cape Client::

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

This is pretty much the full functionality required for our Ctrl+F demo. Now we just need to put it all together.

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
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/html/bootstrap.min.html"
              integrity="sha384-PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb" crossorigin="anonymous">
        <link rel="stylesheet" href="/static/style.html">
        <meta charset="UTF-8">
        <title>Basic AI Powered Ctrl+F Demo</title>
    </head>
    <body>
    <div class="container">
        <div class="col">
            <h1 class="display-1">Cape Ctrl+F Demo</h1>
            <p class="text-muted lead">This super-powered Ctrl+F demo was built using Cape API. View the tutorial <a
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

    <script src="https://code.jQuery.com/jQuery-3.2.1.min.js"
            integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
            crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.3/umd/popper.min.js"
            integrity="sha384-vFJXuSJphROIrBnz7yo7oB41mKfc8JzQZiCq4NCceLEaO4IHwicKwpJf9c9IpFgh"
            crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js"
            integrity="sha384-alpBpkh1PFOepccYVYDB4do5UnbKysX5WZXm3XxPqe5iKTfUKjNkCk9SaVuEZflJ"
            crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.0/jQuery.mark.es6.min.js"></script>
    <script src="/static/app.js"></script>
    </body>
    </html>

Our JavaScript is only a few lines long::

    $(document).ready(function () {
        var doc_text_selector = $('#documentText');
        $.post('/add_document', {'doc': doc_text_selector.text()}); // initialise doc
        var myTimeout = null;
        doc_text_selector.bind('input propertychange', function () {
            $.post('/add_document', {'doc': $(this).text()});
        });
        $('#ctrlfField').bind('input propertychange', function (e) {
            e.preventDefault();
            $(this).addClass('loading');
            if (typeof(myTimeout) !== "undefined") {
                clearTimeout(myTimeout);
            }
            myTimeout = setTimeout(function () {
                $.get('/ctrl_f', {'query': $('#ctrlfField').val()}, function (data) {
                        var answers = data.answers;
                        var answer = {};
                        var range = [];
                        var doc_text = $('#documentText');
                        doc_text.unmark();
                        for (i = 0; i < answers.length; i++) {
                            answer = answers[i];
                            range = {'start': answer.startTextOffset, 'length': (answer.endTextOffset - answer.startTextOffset)};
                            if (i === 0) {
                                doc_text.markRanges([range], {element: 'span', className: 'success'})
                            } else if (i < 4) {
                                doc_text.markRanges([range], {element: 'span', className: 'info'})
                            } else {
                                doc_text.markRanges([range], {element: 'span', className: 'danger'})
                            }
                        }
                        $('#ctrlfField').removeClass('loading');
                    }
                );
            }, 1000);
            return false;
        });
    });

And our stylesheet even shorter::

    .success {
        background: #86f3a0;
    }

    .info {
        background: rgba(23, 162, 184, 0.15);
    }

    .danger {
        background: rgba(23, 162, 184, 0.05);
    }

    .loading {
        background-color: #ffffff;
        background-image: url("http://loadinggif.com/images/image-selection/3.gif");
        background-size: 25px 25px;
        background-position:right center;
        background-repeat: no-repeat;
    }

We can now run the whole thing by typing ``python3 app.py`` in the root of the directory and you are done!















