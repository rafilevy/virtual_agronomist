import os
import csv
from subprocess import Popen, PIPE, STDOUT

from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.document_store.faiss import FAISSDocumentStore
from haystack import Pipeline
from haystack.pipeline import JoinDocuments
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.retriever.dense import DensePassageRetriever
from haystack.retriever.dense import EmbeddingRetriever
from haystack.retriever.dense import BaseRetriever
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.retriever.dense import BaseRetriever
from haystack import file_converter, preprocessor
from .further_question_generator import FurtherQuestionGenerator
from .pipeline_components import QueryClassifier, ContinualDPRNode, TableRetriever, Result
from training.TrainingManager import DPRTrainingManager

from decouple import config


class MLPipeline:
    def __init__(self):
        self.pipeline = None
        self.document_store = None
        self.document_store_faiss = None
        self.question_generator = None

    def write_as4_docs(self):
        converter = file_converter.txt.TextConverter(
            remove_numeric_tables=False,
            valid_languages=["en"])
        knowledgeFilePath = "knowledgeBase/as4-winterBarley.txt"
        as4 = converter.convert(file_path=knowledgeFilePath)

        processor = preprocessor.preprocessor.PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=True,
            split_by="passage",
            split_length=1,
            split_respect_sentence_boundary=False,
            split_overlap=0
        )

        as4Docs = processor.process(as4)
        for i in range(0, len(as4Docs)):
            docMetadata = as4Docs[i]['meta']
            docMetadata["table"] = False
            docMetadata['name'] = knowledgeFilePath
            docMetadata['doucmentID'] = knowledgeFilePath \
                + str(docMetadata['_split_id'])

        self.document_store.delete_all_documents(index='document')
        self.document_store.write_documents(as4Docs)
        self.document_store_faiss.delete_all_documents(index='document')
        self.document_store_faiss.write_documents(as4Docs)
        return (processor, converter)

    def write_table_docs(self, converter, processor):
        data = []
        docs = []

        for file in [file for file in os.listdir("knowledgeBase/tables") if ".csv" in file]:
            with open("knowledgeBase/tables/" + file, mode='r') as infile:
                reader = csv.reader(infile)
                new_dict = {row[0]: row[1:] for row in reader}
                data.append(new_dict)
            infile.close()
            with open("knowledgeBase/tables/" + file[:-4] + ".txt", mode='r') as infile:
                docs.append(infile.read())
            infile.close()

        with open('knowledgeBase/table_text.txt', 'w') as outfile:
            for item in docs:
                outfile.write("%s\n\n" % item)
        outfile.close()

        # Construct FAISS DocumentStore for table content

        tables = converter.convert(file_path="knowledgeBase/table_text.txt")

        tableDocs = processor.process(tables)
        for i in range(len(tableDocs)):
            tableDocs[i]["meta"]["index"] = i
            tableDocs[i]["meta"]["table"] = True

        self.document_store.write_documents(tableDocs)
        self.document_store_faiss.write_documents(tableDocs)
        return data

    def setup(self):
        print("SETTING UP PIPELINE")
        self.document_store = ElasticsearchDocumentStore(
            similarity="dot_product", host="elasticsearch", username="", password="", index="document")
        self.document_store_faiss = FAISSDocumentStore(
            faiss_index_factory_str="Flat",
            return_embedding=True,
            sql_url=f"postgresql://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}:{config('POSTGRES_PORT')}/faiss"
        )
        processor, converter = self.write_as4_docs()
        table_data = self.write_table_docs(converter, processor)

        es_retriever = ElasticsearchRetriever(
            document_store=self.document_store)
        print("SETTING UP DPR")
        dpr_retriever = DPRTrainingManager.get_current_retriever(
            self.document_store_faiss)
        print("SETTING UP EMBEDDINGS")
        embedding_retriever = EmbeddingRetriever(
            document_store=self.document_store_faiss,
            embedding_model="deepset/sentence_bert"
        )
        query_classifier = QueryClassifier()
        print("SETTING UP TABLE")
        table_retriever = TableRetriever(table_data)
        print("SETUP RETRIEVERS")
        self.question_generator = FurtherQuestionGenerator()
        print("UPDATING EMBEDDINGS")
        self.document_store_faiss.update_embeddings(dpr_retriever)
        print("UPDATED EMBEDDINGS")
        self.dpr_node = ContinualDPRNode(
            dpr_retriever, self.document_store_faiss)
        result = Result()
        self.trainer = DPRTrainingManager(
            self.document_store_faiss, self.dpr_node)
        print("SETUP COMPONENTS")
        pipeline = Pipeline()
        pipeline.add_node(component=es_retriever,
                          name="ESRetriever", inputs=["Query"])
        pipeline.add_node(component=self.dpr_node,
                          name="DPRRetriever", inputs=["Query"])
        pipeline.add_node(component=embedding_retriever,
                          name="EmbeddingRetriever", inputs=["Query"])
        pipeline.add_node(component=JoinDocuments(join_mode="merge"), name="JoinResults", inputs=[
                          "DPRRetriever", "EmbeddingRetriever", "ESRetriever"])
        pipeline.add_node(component=query_classifier,
                          name="QueryClassifier", inputs=["JoinResults"])
        pipeline.add_node(component=self.question_generator,
                          name="QnGenerator", inputs=["QueryClassifier.output_1"])
        pipeline.add_node(component=table_retriever, name="TableRetriever", inputs=[
                          "QueryClassifier.output_2"])
        pipeline.add_node(component=result, name="Result", inputs=[
                          "QnGenerator", "TableRetriever"])
        self.pipeline = pipeline
        print("SETUP PIPELINE")

    def answer(self, question, history={}):
        if self.pipeline is None:
            return ""

        print(f"USING HISTORY: {history}")
        self.question_generator.history = history
        responses = self.pipeline.run(
            query=question, top_k_retriever=5)
        return responses[0]

    def report(self, question):
        if self.trainer is None:
            return []
        return self.trainer.processQuestion(question)

    def processTrainingAction(self, question, correct_num):
        if self.trainer is None:
            return 0
        return self.trainer.processTrainingAction(question, correct_num)


shared_pipeline = MLPipeline()
shared_pipeline.setup()
