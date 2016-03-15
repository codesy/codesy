Deployment
==========

codesy is designed with `12-factor app philosophy`_ to run on `heroku`_, so you
can easily deploy your changes to your own heroku app with `heroku toolbelt`_.

Deploy your own
---------------

#. `Create a heroku remote`_. We suggest naming it codesy-`username`::

    heroku apps:create codesy-username

#. Set a ``DJANGO_SECRET_KEY`` on heroku that's unique to you.::

    heroku config:set DJANGO_SECRET_KEY="username-birthdate"

#. Set other required environment variables for heroku::

    heroku config:set DJANGO_DEBUG=True
    heroku config:set ACCOUNT_EMAIL_VERIFICATION=none
    heroku config:set ACCOUNT_DEFAULT_HTTP_PROTOCOL='https'

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

Read the Chrome Extension docs and the Firefox Add-on docs too learn how to
configure them to use https://codesy-username.herokuapp.com.

Deploying to production
-----------------------

We use `Travis CI for continuous deployment to Heroku`_. `Our .travis.yml`_
defines the flow:

#. Commits to ``master`` are tested `on Travis`_.

#. If/when the build passes, the code is automatically deployed to
   https://codesy-stage.herokuapp.com

#. To deploy changes to production, a repo owner pushes a commit to the
   ``production`` branch on GitHub.

This means `anyone` can request a production deployment by submitting a Pull Request from ``master`` to ``production``.



.. _12-factor app philosophy: http://12factor.net/
.. _heroku toolbelt: https://toolbelt.heroku.com/
.. _Create a heroku remote: https://devcenter.heroku.com/articles/git#creating-a-heroku-remote
.. _register your own GitHub App: https://github.com/settings/applications/new
.. _Travis CI for continuous deployment to Heroku: http://blog.travis-ci.com/2013-07-09-introducing-continuous-deployment-to-heroku/
.. _Our .travis.yml: https://github.com/codesy/codesy/blob/master/.travis.yml
.. _on Travis: https://travis-ci.org/codesy/codesy
.. _Request the next deployment: https://github.com/codesy/codesy/compare/production...master?expand=1&title=%5Bdeploy%5D+Request

.. _heroku: https://www.heroku.com/
.. _git hooks: http://git-scm.com/book/en/Customizing-Git-Git-Hooks
