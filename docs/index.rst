.. codesy documentation master file, created by
   sphinx-quickstart on Sun May 18 11:17:00 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome
=======

`codesy <http://codesy.io>`_ is a pay-what-you-want market for the open source community to encourage
coders to fix important bugs.

The code for codesy's API backend combines:

* `GitHub`_ Authentication (via `django-allauth`_)
* `Stripe`_ payments (via `Stripe.js`_)
* codesy variation of `Nate Oostendorp`_'s "`Concurrent Sealed Bid Auction`_"
  system and `CodePatron`_ concept.

.. _GitHub: https://github.com/
.. _django-allauth: https://github.com/pennersr/django-allauth
.. _Stripe: https://stripe.com/
.. _Stripe.js: https://stripe.com/docs/custom-form
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
.. image:: https://raw.githubusercontent.com/codesy/codesy/master/static/img/request-next-deploy.png
   :target: https://github.com/codesy/codesy/compare/production...master?expand=1&title=%5Bdeploy%5D+Request
   :alt: Request Next Deploy

:Code:          https://github.com/codesy/codesy
:License:       AGPLv3; see `LICENSE file
                <https://github.com/codesy/codesy/blob/master/LICENSE>`_
:Documentation: http://codesy.readthedocs.org/
:Issues:        https://github.com/codesy/codesy/issues
:IRC:           irc://irc.freenode.net/codesy
:Mailing list:  https://groups.google.com/forum/#!forum/codesy-dev
:Servers:       https://codesy-stage.herokuapp.com/ (stage)

                https://api.codesy.io/ (prod)

Contents
--------

.. toctree::
   :maxdepth: 2

   development
   deployment
