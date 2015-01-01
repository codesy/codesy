Development
===========

The code for codesy's API backend combines:

* `GitHub`_ Authentication (via `django-allauth`_)
* `Balanced`_ payments (via `balanced.js`_)
* codesy variation of `Nate Oostendorp`_'s "`Concurrent Sealed Bid Auction`_"
  system and `CodePatron`_ concept.

.. _GitHub: https://github.com/
.. _django-allauth: https://github.com/pennersr/django-allauth
.. _Balanced: https://www.balancedpayments.com/
.. _Nate Oostendorp: http://oostendorp.net/
.. _Concurrent Sealed Bid Auction: https://docs.google.com/document/d/1dKYFRTUU6FsX6V4PtWILwN3jkzxiQtbyFQXG75AA4jU/preview
.. _CodePatron: https://docs.google.com/document/d/1fdTM7WqGzUtAN8Hd3aRfXR1mHcAG-WsH6JSwxOqcGqY/preview


Resources
---------
.. image:: https://travis-ci.org/codesy/codesy.png?branch=master
   :target: https://travis-ci.org/codesy/codesy
   :alt: Travis-CI Build Status
.. image:: https://coveralls.io/repos/codesy/codesy/badge.png
    :target: https://coveralls.io/r/codesy/codesy 
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
* `stunnel`_


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

#. Copy `config`_ environment::

    cp .env-dist .env

#. `Migrate`_ DB tables ::

    ./manage.py migrate

#. Create a superuser::

   ./manage.py createsuperuser

#. Start the django app, via plain `runserver`_::

    ./manage.py runserver 127.0.0.1:5000

#. Yay! http://127.0.0.1:5000 works, but there's more to do ...

.. _python: https://www.python.org/
.. _stunnel: https://www.stunnel.org/
.. _Clone: http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _Install requirements: http://pip.readthedocs.org/en/latest/user_guide.html#requirements-files
.. _config: http://12factor.net/config
.. _runserver: https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-runserver


.. _Run https:

Run https
---------

The codesy browser extensions contain content scripts that run on https://
sites and request HTML from the API. So, you'll need to run the backend over
https://. The `easiest way to run https connections with Django`_ is to run
``stunnel`` on https://127.0.0.1:8443 in front of Django:

#. First, run Django dev server in HTTPS mode on port 5000::

    HTTPS=1 python manage.py runserver 127.0.0.1:5000

#. `Install stunnel`_ for your OS (E.g., on Mac OS ``brew install stunnel``).

#. Generate local cert and key file for stunnel::

    openssl req -new -x509 -days 9999 -nodes -out stunnel/stunnel.pem -keyout stunnel/stunnel.pem

#. Run stunnel with the included ``dev_https`` config which proxies
   https://127.0.0.1:8443 to Django on http://127.0.0.1:5000::

    stunnel stunnel/dev_https

#. Go to https://127.0.0.1:8443 to confirm the certificate exception.

Remember to run both ``runserver`` and ``stunnel`` at the same time.

Read the `Chrome Extension docs`_ and the `Firefox Add-on docs`_ too learn how
to configure them to use https://127.0.0.1:8443.

Finally, you'll need to enable GitHub authentication ...

.. _Install stunnel: https://duckduckgo.com/?q=install+stunnel
.. _easiest way to run https connections with Django: http://stackoverflow.com/a/8025645/571420
.. _Chrome Extension docs: https://github.com/codesy/chrome-extension
.. _Firefox Add-on docs: https://github.com/codesy/firefox-addon


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

Now you can sign in with GitHub at https://127.0.0.1:8443.

.. _Add a django-allauth social app: https://127.0.0.1:8443/admin/socialaccount/socialapp/add/

.. _Enable Payments:

Payments
--------

codesy is pre-configured to use the `balanced.js`_ test marketplace. So, you
can use the `test credit card numbers`_ and `test bank accounts`_ from the
balanced docs.

.. _test credit card numbers: https://docs.balancedpayments.com/1.1/overview/resources/#test-credit-card-numbers
.. _test bank accounts: https://docs.balancedpayments.com/1.1/overview/resources/#test-bank-account-numbers

Run the Tests
-------------
Install test requirements::

    pip install -r requirements-test.txt

Running the test suite is easy::

    ./manage.py test -s --noinput --logging-clear-handlers


What to work on
---------------

We have `Issues`_.

If you are an active codesy user, we love getting pull requests that
"`scratch your own itch`_" and help the entire codesy community.

.. _Issues: https://github.com/codesy/codesy/issues
.. _scratch your own itch: https://gettingreal.37signals.com/ch02_Whats_Your_Problem.php


Deploy
------

codesy is designed to run on `heroku`_, so you can easily deploy your changes
to your own heroku app with `heroku toolbelt`_.

#. `Create a heroku remote`_. We strongly suggest naming it codesy-`username`::

    heroku apps:create codesy-username

#. Set a ``DJANGO_SECRET_KEY`` on heroku that's unique to you.::

    heroku config:set DJANGO_SECRET_KEY="username-birthdate"

#. Set a couple more environment variables for heroku::

    heroku config:set DJANGO_DEBUG=True
    heroku config:set ACCOUNT_EMAIL_VERIFICATION=none

#. Push code to the heroku remote::

    git push heroku master

#. `Migrate`_ DB tables::

    heroku run python manage.py migrate

#. Create a superuser::

    heroku run python manage.py createsuperuser

#. To enable GitHub sign-ins on your heroku domain, use the following settings
   to `register your own GitHub App`_:

    * Application name: codesy-username
    * Homepage URL: https://codesy-username.herokuapp.com/
    * Application description: username's codesy
    * Authorization callback URL: https://codesy-username.herokuapp.com/accounts/github/login/callback/

   .. note:: You must use `https`

#. Now go to https://codesy-username.herokuapp.com/admin/socialaccount/socialapp/add/
   to `enable GitHub Auth`_ on *your heroku domain*, using *your* new GitHub App Client ID and Secret

   .. note:: Remember to use `https`

#. That's it. https://codesy-username.herokuapp.com/ should work.


.. _heroku toolbelt: https://toolbelt.heroku.com/
.. _Create a heroku remote: https://devcenter.heroku.com/articles/git#creating-a-heroku-remote
.. _register your own GitHub App: https://github.com/settings/applications/new


.. _Migrate: https://docs.djangoproject.com/en/1.7/topics/migrations/
.. _heroku: https://www.heroku.com/
.. _git hooks: http://git-scm.com/book/en/Customizing-Git-Git-Hooks
.. _balanced.js: https://github.com/balanced/balanced-js
