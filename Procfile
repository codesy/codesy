web: newrelic-admin run-program gunicorn codesy.wsgi
send_mail: python manage.py send_mail
release: ./release-tasks.sh
retry_deferred: python manage.py retry_deferred
runserver: HTTPS=1 python manage.py runserver 127.0.0.1:5000
stunnel: stunnel stunnel/dev_https
