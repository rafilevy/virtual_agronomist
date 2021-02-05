# Agronomist

## About

This was made using the vintasoftware/django-react-boilerplate template - adapted webpack configuration to use typescript. - added Django Channels and runs of Uvicorn instead

## Running

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
