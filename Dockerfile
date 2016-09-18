FROM quay.io/deis/base:0.3.1

RUN apt-get update && apt-get install -y python python-pip python-dev \
    build-essential libffi-dev libpq-dev
WORKDIR /codesy
ADD requirements.txt /codesy/
RUN pip install -r requirements.txt
ADD . /codesy/
CMD newrelic-admin run-program gunicorn -b 0.0.0.0:8000 codesy.wsgi
EXPOSE 8000
