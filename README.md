# Virtual Agronomist

This project is a chat app that can be used to answer agricultural questions - it can be adapted to other domains by changing what knowledge files are used, and by training the models used to answer the questions.

It uses Haystack (https://haystack.deepset.ai/) as its base with some extensions that allow the system to ask the user more questions.

To run everything clone the repository and follow the instructions below

## How to deploy
Navigate to /infrastructure and run the following commands.

### First time using:
-   build the backend:\
	`docker-compose build backend`
-   start postgres and elastisearch container:\
	`docker-compose up postgres`\
	`docker-compose up elasticsearch`
-   add the faiss database:\
	`docker exec -it infrastructure_postgres_1 psql -U fUclnecXsZRakPNYtEGKphYeqoKMgatR -d agronomist`\
	in the prompt enter: `create database faiss;`\
	press CTRL-D to close that
-   Sort out the django migration stuff:\
	`docker-compose run --rm backend python manage.py makemigrations`\
	`docker-compose run --rm backend python manage.py migrate`
-   Create a user for you to login:\
	`docker-compose run --rm backend python manage.py createsuperuser`\
	enter an email and password when prompted

-   Everything should now work! Start it all up \
	`docker-compose up`
   
-   The front end should be at localhost:8000. The admin page is at /insights and will require you to login using the account you created earlier

### After the first setup :
-   You can start it with:\
	`docker-compose up -d elasticsearch`\
	then wait about 5 seconds...\
	`docker-compose up`\
	The script `local.sh` does this for you\
