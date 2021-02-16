FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

# install haystack deps
RUN apt-get update && apt-get install -y curl git pkg-config cmake
RUN pip install farm-haystack
RUN pip install git+https://github.com/deepset-ai/haystack.git
RUN pip install urllib3==1.25.4

RUN apt install libgraphviz-dev graphviz -y
RUN pip install pygraphviz


# Install system dependencies
RUN apt-get update && apt-get install gcc build-essential libpq-dev -y && \
    python3 -m pip install --no-cache-dir pip-tools

WORKDIR /home/user/app/backend

# install python dependencies
ADD *requirements.in /home/user/app/backend/
RUN pip-compile requirements.in > requirements.txt

RUN pip install -r requirements.txt

ADD backend/ /home/user/app/backend

RUN export DJANGO_SETTINGS_MODULE=agronomist.settings.production
RUN mkdir /home/user/.cache
# CMD gunicorn -w 2 agronomist.asgi:application -k uvicorn.workers.UvicornWorker --log-file - -b unix:/home/ap2138/backend/backend/web.sock
CMD uvicorn --reload-dir /home/user/app/backend/chatapp --host 0.0.0.0 --port 8000 agronomist.asgi:application

