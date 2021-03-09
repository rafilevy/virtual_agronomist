# Pipeline Overview

![Pipeline Overview]("../../frontend/img/Pipeline.png")

## pipline.py
`infrastructure/backend/chatapp/pipeline.py` defines the ML pipeline class which implements the general pipeline structure using Haystack.

### State
- `pipeline`: Current instance of pipeline
- `document_store`: ElasticSearch document data structure containing all text documents for ElasticSearch retriever (syntax analysis)
- `document_store_faiss`: FAISS document data structure containing all text documents for DPR and embedding retrievers (semantics analysis)
- `question_generator`: instance of further question generator (imported from `further_questions_generator.py`)

### Methods
- `setup()` initialises of the entire pipeline.
- `answer(string question)`  triggers the question answering pipeline with a question input
- `report(string question)` handles the unsatisfying answers reported by users
- `processTrainingAction(string question, int correct_num)` handles the generation of new training data generated from user responses

The query is first parsed to extract keywords about variety (if there is any) and transform the question into a more general question about a crop (e.g. from Dunston to Winter Wheat).

The question is then passed to three Retrievers to extract relevant documents based on syntactic and semantic characteristics. The results are joint based on relative confident scores. The top 20 extracted documents will then go to the query classifier, which decides whether to progress with further questions (see further_question_generator.py below), or a table lookup to extract information from the table database based on the content of the most likely document extracted. The table retriever will on the other hand utilise a [BERT-based TAPAS](https://huggingface.co/google/tapas-base-finetuned-wtq") model from Google Research to perform a single lookup into the relevant table.

The final result will be passed to the backend for display.

## further_questions_generator.py
`infrastructure/backend/chatapp/further_questions_generator.py` defines the further question generator in the `FurtherQuestionGenerator` class.

### State
- `history`: record of further questions generated and responses from the user
- `parser`: instance of question parser to detect crop variety keywords
- `pressure_score_generator`: instance of pressure score generator

### Methods

- `update_components()` updates the pressure score system, keywords settings after new csv documents are uploaded.
- `question_parsing(string text)` extracts crop variety keywords and parses the question to more general one with crop replacing variety
- `generate_keywords（string text)` generate variety keywords from the text
- `individualFiltersGenerator(string text)` generates keywords dictionary for timing, crop, area, sowing time, etc.
- `topDocsFilterGenerator(Document[] docs)` batch generates keywords dictionary for multiple document segments
- `filters_difference(self, filters_list, specified=[])` computes the differences between keywords set, i.e. if two documents have keywords in the same category but different value.

It will extract keywords (see `KeyInfoExtractor.py` below) in both the question asked and the extracted document and compare the context detected. If there is a difference among the documents, further questions will be asked to further determine the most probable answer to the question. 

## pressure_score_generator.py
`infrastructure/backend/chatapp/pressure_score_generator.py` defines the PressureScoreGenrator class which generates and calculates the pressure score based on questions from pressure_score.csv and responses from the users.

### Methods

- `update_pressure_table()` updates the question system when a new .csv file is uploaded.
- `calculate_pressure_score()` generates relevant questions and calculates the score based on responses from the user.

## KeyInfoExtractor.py
`infrastructure/backend/chatapp/KeyInfoExtractor.py` 

### Class
`KeywordExtractor`

### State

- `key_infos`: a list of KeyInfo objects (see below). Each object stores a category’s information

### Methods

- `read_key_info_file(String filename, boolean verbose)`
    - Reads the csv at filename (for example `categories.csv`)
    - `Verbose` - default `false`, if set `true`, each category read will be printed.
- `check_current_categories(boolean verbose)`
    - Prints all category names
    - `Verbose` - default `false`, if set `true`, questions and values printed as well
- `get_best_matches(string phrase)`
    - Takes a phrase (question or document), returns a list of extracted (category: keywords) pairs.

### Internal Utility Methods
- `merge_dicts(dict dict1, dict dict2)`
- `add_key_info_categories(KeyInfo[] key_is)`
- `add_key_info_category(KeyInfo[] key_info)`
- `standardise_format(string phrase)`
- `get_best_match(dict diction)`
- `make_dict(string[] one_grams,string[] target_one_grams,string[] - target_completes)`
- `reduce_run(string[] run, string[] completes)`

### Class
`KeyInfo`

### State
- `name`: `string`, name of one category
- `one_grams`: `string[]`, all words appearing in values for one - category
- `completes`: `string[]`, all values for one category 
- `question`: `string`, the generic question for this category

This file contains the keyword extractor. This is used in the further question generator, on both the possible answers and the question. 
