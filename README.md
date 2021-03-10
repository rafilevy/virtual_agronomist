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

## Logs

Logs include timestamps, questions and given answers. Logs are committed to the database every time a user completes a question answer cycle with the system.
A complete log file can be downloaded from the admin page.

## File Uploads and formatting

In the admin page, files can be uploaded to add information into the knowledge base or to configure the keyword extraction, timing translation and pressure score calculation. The format requirements for the files are as following:

### Text-based documents

Any new text-based document should be reformatted such that each paragraph contains one knowledge point and is phrased independently with no reference to other paragraphs or contexts. The more relevant keywords mentioned, the better the document is defined and it will improve the accuracy when related questions are asked. 
For example, it is useful to explicitly mention if any specific fungicide is relevant to the discussion, or the timing currency in discussion. Mentioning key things defined in the categories.csv(refer to file format below) file will improve the accuracy in sensing the context of the paragraph.

This file should be a `.txt` file with the name describing the contents. Explicit mentioning of a crop name is preferred as it will provide a clearer definition for the information. For example, the name of the file can be `Winter Wheat Fungicide.txt`.

### table-based documents

Any table based document should be a pair of .csv and .txt files with the same file name and describes information from one single table. Each entry in the csv should describe one row/column in the table.
For example, the following table can be represented by the csv entries below:

The associated .txt file should contain the description of the table. Following the example above, the .txt file can be:

The more specific the description, the more accurate it will be when a question about the table is asked. The connection between the description and the actual table is detected by the shared filename, but the filename itself does not matter. For example, table1.csv and table1.txt works just fine as valid filename and there is no difference if the pair is renamed to components.csv and components.txt.

### Keyword Extractor - `categories.csv`

The keyword extractor is used to tag passages of text with pairs of categories and keywords, for example (crop: winter barley, winter wheat) is such a pair.
In addition, the keyword extractor can provide a generic question for each category. To extract the correct keywords and their corresponding keywords, the file `categories.csv` is used. Each row of the csv file contains the information for one category. The information for each category is:
-   1 Category Name - (e.g. crop, fungicide)
-   1 Generic Question - (e.g. Is there a specific crop that you would like to ask about?)
-   1 or more values for this category - (e.g. spring wheat| winter wheat| spring beans)

In order to allow questions to contain commas, the separating character for this file is a pipe symbol (| ). This should come immediately after the end of a value. There should be no separating character at the end of a line. There can be spaces before a new value. Category names and values can be input in uppercase or lowercase, but all output will be in lowercase only.
Below is an example of some truncated rows of a `categories.csv` file.

```
Crop| Is there a specific crop that you would like to ask about?| spring wheat| winter wheat| winter barley
Disease| Is there a specific disease that you would like to ask about?| ramularia| septoria| rust| yellow rust
Fungicide| Do you want to check for a specific fungicide?| opus| bowman| cortez| rubric| epic| corral| amber
Timing| Is there a specific timing that you would like to ask about? (E.g. T0,T1,etc)| t0| t1| t2| t3| t4
Area| Which area are you in? (E.g. east/north/etc)| east| north| southeast| west| south| southwest
```

Categories may be added by adding a new row with the required information. 

### Timing translator - `translation.csv`

The timing translator is used to standardise crop timing names. It does this by grouping equivalent timing names together, within each crop. The translation.csv file is comma-separated. For each crop’s translation table, multiple rows are used. The information for each crop is:
-   1 unique Crop Name
-   1 or more lists of equivalent timings
⋅⋅⋅The first name should be unique within this crop
⋅⋅⋅Each timing name is separated by a comma
-   1 or more values for this category - (e.g. spring wheat| winter wheat| spring beans)

Each crop’s translation table is therefore represented by 2 or more lines. Translation tables should be separated by a blank line. Below is an example of timing tables for winter wheat and spring wheat.

`Winter Wheat`

`T0, leaf 4`

`T1, leaf 3`

`T1.5, leaf 2`

`T2, flag leaf`

`T3, ear`

`T4, second ear`

`Spring Wheat`

`T0`

`T1`

`T2`

`T3`

This extract shows a sample translation table for winter wheat. This translation table will standardise leaf 4 to T0 if the crop is known to be winter wheat. There can be more than one translation per line, for example replacing line 2 with T0, leaf 4, leaf four would lead to the translator standardising both leaf 4 and leaf four to T0. In the second table, no translations have been added.

#### Pressure Score Calculator - `pressure_score.csv`

The pressure score calculator is used to calculate the pressure score of the user’s current situation based on a series of predefined questions. This will be triggered when different pressure scores are mentioned in the top extracted documents. The set of questions and scores related to each option is configurable with the `pressure_score.csv`.

Any question in the pressure score system is defined by multiple entries, each having four fields separated by a comma:
-   1 Crop Name - (e.g. winter wheat, winter barley)
-   1 Factor - (e.g. area in the country, variety of crop, sowing date)
-   1 Option - (e.g.(area in the country) East, West)
-   1 Score related to the Option

Below is the example of a set of entries which forms a question for the pressure score calculation of winter wheat.

`winter wheat,area in the country,East,1`

`winter wheat,area in the country,North,2`

`winter wheat,area in the country,South East,2`

`winter wheat,area in the country,West,3`

`winter wheat,area in the country,South,3`

`winter wheat,area in the country,South West,4`

When the pressure score calculator is triggered for a question on winter wheat, these entries will form a question about the location of the user in the country. If the user responds with the East option, the current pressure score will be increased by 1. If the response is West, the pressure score will be increased by 3.

When new entries are added to the file, the pressure score system will be updated and new questions can be asked.


