Development
===========

The code for codesy's API backend combines:

* `GitHub`_ Authentication (via `django-allauth`_)
* `Balanced`_ payments (via `balanced-python`_)
* codesy variation of `Nate Oostendorp`_'s "`Concurrent Sealed Bid Auction`_"
  system and `CodePatron`_ concept.

.. _GitHub: https://github.com/
.. _django-allauth: https://github.com/pennersr/django-allauth
.. _Balanced: http://balancedpayments.com/
.. _balanced-python: https://github.com/balanced/balanced-python
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
:License:       AGPLv3; see LICENSE file
:Documentation: http://codesy.readthedocs.org/
:Issues:        https://github.com/codesy/codesy/issues
:IRC:           irc://irc.freenode.net/codesy
:Mailing list:  https://groups.google.com/forum/#!forum/codesy-dev
:Servers:       https://codesy-dev.herokuapp.com/ (dev)

                https://codesy-stage.herokuapp.com/ (stage)

                https://codesy.io/ (prod)

                https://whatsdeployed.paas.allizom.org/?owner=codesy&repo=codesy&name[]=Dev&url[]=https://codesy-dev.herokuapp.com/revision.txt&name[]=Stage&url[]=https://codesy-stage.herokuapp.com/revision.txt&name[]=Prod&url[]=https://codesyio/revision.txt (What's Deployed)


Requirements
------------

* `python`_
* (suggested) `foreman`_
* (suggested) `autoenv`_


Get Started
-----------

codesy's API backend is designed to be run on `heroku`_, so you can also run it locally with `foreman`_:

#. Clone::

    git clone git@github.com:codesy/codesy.git

#. Create and activate virtual environment::

    virtualenv codesy/env
    source codesy/env/bin/activate

#. Install requirements::

    pip install -r requirements.txt

#. Copy, configure, & export codesy environment variables (easier with `autoenv`_)::

    mv codesy/.env-dist codesy/.env
    vim codesy/.env
    cd codesy
    source .env

#. Create DB tables::

    ./manage.py syncdb
    ./manage.py migrate

#. Start the django app via `foreman`_::

    foreman start

.. _python: https://www.python.org/
.. _foreman: https://github.com/ddollar/foreman
.. _autoenv: https://github.com/kennethreitz/autoenv
.. _ReadTheDocs: http://codesy.readthedocs.org/en/latest/development.html

Run the Tests
-------------

Running the test suite is easy::

    ./manage.py test -s --noinput --logging-clear-handlers

Deploy
------

TODO: Fill in deployment steps for `heroku`_

What to work on
---------------

We have `Issues`_.

If you are an active codesy user, we love getting pull requests that "`scratch your own itch`_" and help the entire codesy community.

.. _scratch your own itch: https://gettingreal.37signals.com/ch02_Whats_Your_Problem.php
.. _heroku: https://www.heroku.com/
.. _Issues: https://github.com/codesy/codesy/issues
