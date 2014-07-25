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

codesy's API backend tries to be very slim, so starting should be easy:

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

#. `Sync`_ first DB tables (be sure to create a superuser)::

    ./manage.py syncdb

#. `migrate`_ remaining DB tables::

    ./manage.py migrate

#. Start the django app, via plain `runserver`_::

    ./manage.py runserver 0.0.0.0:5000

   or via `foreman`_::

    foreman start

#. Yay! http://127.0.0.1:5000 works, but there's more to do ...

.. _python: https://www.python.org/
.. _foreman: https://github.com/ddollar/foreman
.. _Clone: http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _Install requirements: http://pip.readthedocs.org/en/latest/user_guide.html#requirements-files
.. _config: http://12factor.net/config
.. _runserver: https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-runserver


.. _Enable GitHub Auth:

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

.. _Enable Payments:

Enable Payments Sandbox
-----------------------

To enable a BrainTree sandbox so you can work with payments:

#. `Sign up for a BrainTree Sandbox <https://www.braintreepayments.com/get-started>`_

#. Put your Merchant ID, Public Key, and Private Key into your `.env` file
   (copied from `.env-dist <https://github.com/codesy/codesy/blob/master/.env-dist>`_)

#. Source the `.env` file to export codesy environment variables (again, automated by `autoenv`_)::

    source .env

Now you can deposit (fake) funds at http://127.0.0.1:5000

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


Deploy
------

codesy is designed to run on `heroku`_, so you can easily deploy your changes
to your own heroku app with `heroku toolbelt`_.

#. `Create a heroku remote`_::

    heroku apps:create codesy-<username>

#. Set a ``DJANGO_SECRET_KEY`` for heroku::

    heroku config:set DJANGO_SECRET_KEY="username-birthdate"

#. Set a couple more environment variables for heroku::

    heroku config:set DJANGO_DEBUG=True
    heroku config:set ACCOUNT_EMAIL_VERIFICATION=none

#. Push code to the heroku remote::

    git push heroku master

#. `Sync`_ first DB tables (be sure to create a superuser)::

    heroku run python manage.py syncdb

#. `migrate`_ remaining DB tables::

    heroku run python manage.py migrate

#. To enable GitHub sign-ins on your heroku domain, use the following settings to `register your own GitHub App`_

    * Application name: codesy-username
    * Homepage URL: https://codesy-username/herokuapp.com/
    * Application description: username's codesy
    * Authorization callback URL: https://codesy-username.herokuapp.com/accounts/github/login/callback/

   .. note:: You must use `https`

#. Now go to https://codesy-username.herokuapp.com/admin/socialaccount/socialapp/add/
   to `enable GitHub Auth`_ on *your heroku domain*, using *your* new GitHub App Client ID and Secret

   .. note:: Remember to use `https`

#. `Enable Payments`_ as above, using heroku environment variables::

    heroku config:set BRAINTREE_MERCHANT_ID=""
    heroku config:set BRAINTREE_PUBLIC_KEY=""
    heroku config:set BRAINTREE_PRIVATE_KEY=""

#. That's it. https://codesy-username.herokuapp.com/ should work.


.. _heroku toolbelt: https://toolbelt.heroku.com/
.. _Create a heroku remote: https://devcenter.heroku.com/articles/git#creating-a-heroku-remote
.. _Generate: http://www.miniwebtool.com/django-secret-key-generator/
.. _register your own GitHub App: https://github.com/settings/applications/new


.. _Sync: https://docs.djangoproject.com/en/1.6/ref/django-admin/#syncdb
.. _migrate: http://south.readthedocs.org/en/latest/commands.html#migrate
.. _heroku: https://www.heroku.com/
.. _autoenv: https://github.com/kennethreitz/autoenv
.. _git hooks: http://git-scm.com/book/en/Customizing-Git-Git-Hooks


Tips
----

We have some useful `git hooks`_. After you clone, link them all::

    rm -rf .git/hooks
    ln -s git-hooks .git/hooks
