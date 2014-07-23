Development
===========

The code for codesy's API backend combines:

* `GitHub`_ Authentication (via `django-allauth`_)
* `Braintree`_ payments (via `braintree python library`_)
* codesy variation of `Nate Oostendorp`_'s "`Concurrent Sealed Bid Auction`_"
  system and `CodePatron`_ concept.

.. _GitHub: https://github.com/
.. _django-allauth: https://github.com/pennersr/django-allauth
.. _Braintree: https://www.braintreepayments.com/
.. _braintree python library: https://developers.braintreepayments.com/javascript+python
.. _Nate Oostendorp: http://oostendorp.net/
.. _Concurrent Sealed Bid Auction: https://docs.google.com/document/d/1dKYFRTUU6FsX6V4PtWILwN3jkzxiQtbyFQXG75AA4jU/preview
.. _CodePatron: https://docs.google.com/document/d/1fdTM7WqGzUtAN8Hd3aRfXR1mHcAG-WsH6JSwxOqcGqY/preview


Resources
---------
.. image:: https://travis-ci.org/codesy/codesy.png?branch=master
   :target: https://travis-ci.org/codesy/codesy
   :alt: Travis-CI Build Status

.. image:: https://requires.io/github/codesy/codesy/requirements.png?branch=master
   :target: https://requires.io/github/codesy/codesy/requirements/?branch=master
   :alt: Requirements Status

:Code:          https://github.com/codesy/codesy
:License:       AGPLv3; see `LICENSE file
                <https://github.com/codesy/codesy/blob/master/LICENSE>`_
:Documentation: http://codesy.readthedocs.org/
:Issues:        https://github.com/codesy/codesy/issues
:IRC:           irc://irc.freenode.net/codesy
:Mailing list:  https://groups.google.com/forum/#!forum/codesy-dev
:Servers:       https://codesy-dev.herokuapp.com/ (dev)

                https://codesy-stage.herokuapp.com/ (stage)

                https://codesy.io/ (prod)

                https://whatsdeployed.paas.allizom.org/?owner=codesy&repo=codesy&name[]=Dev&url[]=https://codesy-dev.herokuapp.com/revision.txt&name[]=Stage&url[]=https://codesy-stage.herokuapp.com/revision.txt (What's Deployed)


Requirements
------------

* `python`_
* (suggested) `foreman`_
* (suggested) `autoenv`_


Get Started
-----------

codesy's API backend is configured to run on `heroku`_, so you can start easily with `foreman`_:

#. `Clone`_::

    git clone git@github.com:codesy/codesy.git
    cd codesy

#. Create and activate `virtual environment`_::

    virtualenv env
    source env/bin/activate

#. `Install requirements`_::

    pip install -r requirements.txt

#. Copy & source `config`_ environment (`autoenv`_ automates this when you change directories)::

    cp .env-dist .env
    source .env

#. `Sync`_ and `migrate`_ DB tables (be sure to create a superuser)::

    ./manage.py syncdb
    ./manage.py migrate

#. Start the django app via `foreman`_::

    foreman start

#. Yay! http://127.0.0.1:5000 works, but there's more to do ...

.. _python: https://www.python.org/
.. _foreman: https://github.com/ddollar/foreman
.. _Clone: http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _Install requirements: http://pip.readthedocs.org/en/latest/user_guide.html#requirements-files
.. _config: http://12factor.net/config
.. _Sync: https://docs.djangoproject.com/en/1.6/ref/django-admin/#syncdb
.. _migrate: http://south.readthedocs.org/en/latest/commands.html#migrate


Enable GitHub Auth
------------------

To enable GitHub authentication, you can use our codesy-local OAuth app.

`Add a django-allauth social app`_ for GitHub:

* Provider: GitHub
* Name: codesy-local
* Client id: c040becacd90c91a935a
* Secret key: 08c3da1421bb280e6fa5f61c05afd0c3128a2f9f
* Sites: example.com -> Chosen sites

Now you can sign in with GitHub at http://127.0.0.1:5000. Still more ...

.. _Add a django-allauth social app: http://127.0.0.1:5000/admin/socialaccount/socialapp/add/

Enable Payments Sandbox
-----------------------

To enable a BrainTree sandbox so you can work with payments:

#. `Sign up for a BrainTree Sandbox <https://www.braintreepayments.com/get-started>`_

#. Put your Merchant ID, Public Key, and Private Key into your `.env` file
   (copied from `.env-dist <https://github.com/codesy/codesy/blob/master/.env-dist>`_)

#. Source the `.env` file to export codesy environment variables (again, automated by `autoenv`_)::

    source .env

Run the Tests
-------------

Running the test suite is easy::

    ./manage.py test -s --noinput --logging-clear-handlers


What to work on
---------------

We have `Issues`_.

If you are an active codesy user, we love getting pull requests that 
"`scratch your own itch`_" and help the entire codesy community.

.. _scratch your own itch: https://gettingreal.37signals.com/ch02_Whats_Your_Problem.php
.. _Issues: https://github.com/codesy/codesy/issues


Tips
----

We have some useful `git hooks`_. After you clone, link them all::

    rm -rf .git/hooks
    ln -s git-hooks .git/hooks


Deploy
------

TODO: Fill in deployment steps for `heroku`_

.. _heroku: https://www.heroku.com/
.. _autoenv: https://github.com/kennethreitz/autoenv
.. _git hooks: http://git-scm.com/book/en/Customizing-Git-Git-Hooks
