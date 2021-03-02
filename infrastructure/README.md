# Agronomist

## About

This was made using the vintasoftware/django-react-boilerplate template - adapted webpack configuration to use typescript. - added Django Channels and runs of Uvicorn instead

## Running

### First time using:
-   build the backend:
     docker-compose build backend
-   start postgres and elastisearch container
     docker-compose up postgres
     docker-compose up elasticsearch
-   add the faiss database
     docker exec -it infrastructure_postgres_1 psql -U fUclnecXsZRakPNYtEGKphYeqoKMgatR -d agronomist
     in the prompt enter: create database faiss;
     press CTRL-D to close that
-   Sort out the django migration stuff!
     docker-compose run --rm backend python manage.py makemigrations
     docker-compose run --rm backend python manage.py migrate
-   Create a user for you to login
     docker-compose run --rm backend python manage.py createsuperuser
     enter an email and password when prompted

-   Everything should now work! Start it all up
     docker-compose up

-   After the first setup you can start it with:
     docker-compose up -d elasticsearch
     then wait about 5 seconds...
     docker-compose up


### Setup

-   Create the migrations:  
    `docker-compose run --rm backend python manage.py makemigrations`
-   Run the migrations:
    `docker-compose run --rm backend python manage.py migrate`
-   Can also be run by exec'ing into the backend container

-   Open a command line window and go to the project's directory.
-   `docker-compose up -d`
    To access the logs for each service run `docker-compose logs -f service_name` (either backend, frontend, etc)

### Adding packages

-   To install a new npm package you can create a bash session inside the running `frontend` container: `docker exec -it container_name bash`
-   To install a new PyPi package you will have to update the `requirements.in` file and rebuild the `backend` container.
