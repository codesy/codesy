Development
===========

Requirements
------------

* `python`_
* `stunnel`_


Install Locally
---------------

codesy's backend tries to be very slim, so starting should be easy.
(Especially if you're familiar with Django):

#. `Clone`_ and change to the directory::

    git clone git@github.com:codesy/codesy.git
    cd codesy

#. Create and activate a `virtual environment`_::

    virtualenv env
    source env/bin/activate

#. `Install requirements`_::

    pip install -r requirements.txt

#. Copy `decouple`_ `config`_ env file::

    cp .env-dist .env

#. `Migrate`_ DB tables ::

    ./manage.py migrate

#. `Create a superuser`_::

   ./manage.py createsuperuser



.. _python: https://www.python.org/
.. _stunnel: https://www.stunnel.org/
.. _Clone: http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _Install requirements: http://pip.readthedocs.org/en/latest/user_guide.html#requirements-files
.. _decouple: https://pypi.python.org/pypi/python-decouple
.. _config: http://12factor.net/config
.. _Create a superuser: https://docs.djangoproject.com/en/1.7/ref/django-admin/#django-admin-createsuperuser


.. _Run https:

Run locally with https
----------------------

The codesy browser extensions contain content scripts that execute on https://
domains and request resources from the codesy domain. So, you need to run the
backend over https://. The `easiest way to run https connections with Django`_
is to run ``stunnel`` on https://127.0.0.1:8443 in front of Django:

#. First, `install stunnel`_ for your OS (E.g., on Mac OS ``brew install stunnel``).

#. Run Django dev server **in HTTPS mode** on port 5000::

    HTTPS=1 ./manage.py runserver 127.0.0.1:5000

#. Generate local cert and key file for stunnel::

    openssl req -new -x509 -days 9999 -nodes -out stunnel/stunnel.pem -keyout stunnel/stunnel.pem

#. Run stunnel with the included ``dev_https`` config::

    stunnel stunnel/dev_https

#. Go to https://127.0.0.1:8443 and confirm the certificate exception.

.. note:: You always need to run both ``runserver`` and ``stunnel``.

#. Change the `default django Site record`_ from ``example.com`` to ``127.0.0.1:8443``

Read the `Chrome Extension docs`_ and the `Firefox Add-on docs`_ too learn how
to configure them to use https://127.0.0.1:8443.

Finally, you'll need to enable GitHub authentication ...

.. _install stunnel: https://duckduckgo.com/?q=install+stunnel
.. _easiest way to run https connections with Django: http://stackoverflow.com/a/8025645/571420
.. _default django Site record: https://127.0.0.1:8443/admin/sites/site/1/
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

codesy is pre-configured to use the `Stripe`_ test marketplace. So, you
can use the `test credit card numbers`_ from the Stripe docs.

.. _Stripe: https://stripe.com/
.. _test credit card numbers: https://stripe.com/docs/testing#cards

Run the Tests
-------------
Install test requirements::

    pip install -r requirements-test.txt

Running the test suite is easy::

    ./manage.py test -s --noinput --logging-clear-handlers


Working on Docs
---------------
Install dev requirements::

    pip install -r requirements-dev.txt

Building the docs is easy::

    cd docs
    sphinx-build . html

Read the beautiful docs::

    open html/index.html


What to work on
---------------

We have `Issues`_.

If you are an active codesy user, we love getting pull requests that
"`scratch your own itch`_" and help the entire codesy community.

.. _Issues: https://github.com/codesy/codesy/issues
.. _scratch your own itch: https://gettingreal.37signals.com/ch02_Whats_Your_Problem.php
