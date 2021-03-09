# Infrastructure

The `docker-compose` file outlines the different containers used to bring the project together. Note this is for development use only, though a production configuration exists for the backend container.

## Frontend
The frontend container will watch for changes in the `./frontend` folder, recompile and hot-reload code being served at localhost:3000.

## Backend

The backend container is built from `./backend ` folder and starts a Django web app using Uvicorn to allow for web-socket connections as well as http ones.

`/chatapp` contains the Django app where most logic resides (which should in future be refactored).

This is in part because we have decided to have the chat handling system as well as the ML pipeline live on the same machine while this would be unfeasible in a production setup.

Recommendation would be to use a combination Celery workers to handle the shared_pipeline, and async functions with Django Channels to be able to handle other chat communications while pipeline results are waited on.
However care would need to be taken when updating the document store with potentially multiple pipelines alive.

- `url.py` dictates the HTTP urls that the application responds to.

- `views.py` specifies the HTTP api that the applications exposes as well the endpoints to serve up the chat app and admin static index files.

- `models.py` specifies the PreTrainingData model that allows for persistence of training data. Care should be taken that the persisted data will be obsolete if the document store is reloaded (i.e. has new IDs). It also specifies the `RequestRecord` model for logging completed requests made to the system.

- `/users` contains a custom User model if in future different data is wanted to be collected.

- The rest of the top level folders are boilerplate Django (unless specified elsewhere in the documentation). However notably `agronomist/urls.py` is the initial entry-point for the urls that the web app serves. 

- `asgi.py` includes the Django Channels configuration code to allow the `chatapp/consumers.py` to handle websocket connections at the path `/ws/chat/`.

- `js-build` is meant for production builds of the React app - there is a corresponding webpack configuration file in the frontend folder.