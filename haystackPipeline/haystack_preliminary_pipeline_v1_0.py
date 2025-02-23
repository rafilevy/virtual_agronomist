# Check for running GPU
!nvidia-smi

#run once for initial installs
! pip install farm-haystack
! pip install git+https://github.com/deepset-ai/haystack.git
! pip install urllib3==1.25.4
! pip install torch==1.6.0+cu101 torchvision==0.6.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html

#Start Elasticsearch from source
! wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.2-linux-x86_64.tar.gz -q
! tar -xzf elasticsearch-7.6.2-linux-x86_64.tar.gz
! chown -R daemon:daemon elasticsearch-7.6.2

# Connect to Elasticsearch
import os
from subprocess import Popen, PIPE, STDOUT
es_server = Popen(['elasticsearch-7.6.2/bin/elasticsearch'],
                   stdout=PIPE, stderr=STDOUT,
                   preexec_fn=lambda: os.setuid(1)
                  )
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")

from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader

# Testing with tutorial data
doc_dir = "data/article_txt_got"
s3_url = "https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/wiki_gameofthrones_txt.zip"
fetch_archive_from_http(url=s3_url, output_dir=doc_dir)
dicts = convert_files_to_dicts(dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)

# Connecting point to preprocessing of as4
document_store.write_documents(dicts)

# Fast filter to narrow down text - Default BM25, can be cunstomised
from haystack.retriever.sparse import ElasticsearchRetriever
retriever = ElasticsearchRetriever(document_store=document_store)

# Reader to further scan with Hugging Face models
# reader = TransformersReader(model_name_or_path="distilbert-base-uncased-distilled-squad", tokenizer="distilbert-base-uncased", use_gpu=-1)
reader = FARMReader(model_name_or_path="deepset/bert-large-uncased-whole-word-masking-squad2", use_gpu=True)

from haystack.pipeline import ExtractiveQAPipeline

# Original Finder deprecated, pipeline allows more flexibility
# prediction = finder.get_answers(question="Who is the father of Arya Stark?", top_k_retriever=10, top_k_reader=5)

# top_k_retriever -> the more retriever the more document scanned in Reader, slower but higher hit rate
extractive_pipeline = ExtractiveQAPipeline(reader=reader, retriever=retriever) # Other options: Document Search, Generative, FAQ

question = input("What would you like to ask? ")
prediction = extractive_pipeline.run(query=question, top_k_retriever=10, top_k_reader=5)
# print_answers(prediction, details="all") #details: all, medium, minimal
# data format: {query,'answers':[{'answer','score','probability','context','document_id','offset','meta'}]}
print(prediction['answers'][0]['answer'])
