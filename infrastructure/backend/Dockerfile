FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user
WORKDIR /home/user/app/backend

# Install system dependencies
RUN apt-get update && apt-get install gcc build-essential libpq-dev -y && \
    python3 -m pip install --no-cache-dir pip-tools

# install python dependencies
ADD *requirements.in /home/user/app/backend/
RUN pip-compile requirements.in > requirements.txt

RUN pip install -r requirements.txt

ADD backend/ /home/user/app/backend

USER user
RUN export DJANGO_SETTINGS_MODULE=agronomist.settings.production
# CMD gunicorn -w 2 agronomist.asgi:application -k uvicorn.workers.UvicornWorker --log-file - -b unix:/home/ap2138/backend/backend/web.sock
CMD uvicorn --reload --host 0.0.0.0 --port 8000 agronomist.asgi:application

