import os
from subprocess import Popen, PIPE, STDOUT
from threading import RLock
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack import Pipeline
from haystack.pipeline import JoinDocuments
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.retriever.dense import DensePassageRetriever
from haystack.retriever.dense import EmbeddingRetriever
from haystack.retriever.dense import BaseRetriever
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
import haystack
from training.TrainingManager import DPRTrainingManager


class ResponseRequiredException(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class CustomRetriever(BaseRetriever):
    def retrieve(self, query, filters=None, top_k=10, index=None):
        super().retrieve(query, filters, top_k, index)
        # placeholder retriever
        return []


filters_dictionary = {"timings": ["t0", "t1", "t2", "t3"],
                      "fungus": ["ramularia", "yellow rust"],
                      "areas": ["east", "north", "southeast", "west", "south", "southwest"]}
questions = {"timings": "Is there a specific timing that you would like to ask about? (E.g. T0, T1, etc)",
             "fungus": "Is there a fungi type that you would want to know about specifically?",
             "area": "Which area are you in? (E.g. east, north, etc)"}


class FurtherQuestionGenerator:
    outgoing_edges = 1

    def __init__(self):
        self.history = {}

    def individualFiltersGenerator(self, text):
        current_filters = {}
        for category, filters in filters_dictionary.items():
            for filter in filters:
                if filter in text.lower():
                    if category in current_filters:
                        current_filters[category].append(filter)
                    else:
                        current_filters[category] = [filter]
        return current_filters

    def topDocsFilterGenerator(self, docs):
        return [self.individualFiltersGenerator(doc.text) for doc in docs]

    def filters_difference(self, filters_list, specified=[]):
        current_filters = {}
        for filters in filters_list:
            for category, filters in filters.items():
                if ((category not in specified) and (category in current_filters) and (filters != current_filters[category])):
                    return category
                elif ((category not in specified) and (category not in current_filters)):
                    current_filters[category] = filters
        return None

    def furtherQuestions(self, docs, specified=[]):
        filters_list = self.topDocsFilterGenerator(docs)
        match = [0 for doc in docs]
        keyword = self.filters_difference(filters_list, specified)
        while keyword is not None:
            new_key = None
            if (questions[keyword] in self.history):
                new_key = self.history[questions[keyword]]
            else:
                raise ResponseRequiredException(questions[keyword])
            match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (new_key.lower(
            ) in filters_list[i][keyword])) else match[i] for i in range(len(filters_list))]
            match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (filters_list[i][keyword] == [
                                      new_key.lower()])) else match[i] for i in range(len(filters_list))]
            specified.append(keyword)
            keyword = self.filters_difference(filters_list, specified)
        return [x for _, x in sorted(zip(match, docs), key=lambda pair: pair[0], reverse=True)]

    def run(self, *args, **kwargs):
        specified = list(self.individualFiltersGenerator(
            kwargs["query"]).keys())
        return (self.furtherQuestions(kwargs["documents"], specified), "output_1")


class ContinualDPRNode:
    outgoing_edges = 1

    def __init__(self, retriever, document_store):
        self.retriever = retriever
        self.document_store = document_store
        self.lock = RLock()

    def update_retriever(self, retriever):
        with self.lock:
            self.document_store.update_embeddings(retriever)
            self.retriever = retriever

    def run(self, *args, **kwargs):
        with self.lock:
            return self.retriever.run(*args, **kwargs)


class MLPipeline:
    def __init__(self):
        self.pipeline = None
        self.document_store = None
        self.question_generator = None

    def setup(self):
        print("SETTING UP PIPELINE")
        converter = haystack.file_converter.txt.TextConverter(
            remove_numeric_tables=False,
            valid_languages=["en"])

        knowledgeFilePath = "../knowledgeBase/as4-winterBarley.txt"
        as4 = converter.convert(file_path=knowledgeFilePath)

        processor = haystack.preprocessor.preprocessor.PreProcessor(
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
            docMetadata['name'] = knowledgeFilePath
            docMetadata['doucmentID'] = knowledgeFilePath \
                + str(docMetadata['_split_id'])

        print("PROCESSED AS4 DOCS")
        self.document_store = ElasticsearchDocumentStore(
            similarity="dot_product", host="elasticsearch", username="", password="", index="document")
        print("DELETED PREVIOUS DOCUMENTS")
        self.document_store.delete_all_documents(index='document')
        self.document_store.write_documents(as4Docs)
        print("WRITTEN DOCUMENT")
        es_retriever = ElasticsearchRetriever(
            document_store=self.document_store)
        dpr_retriever = DPRTrainingManager.get_current_retriever(
            self.document_store)
        embedding_retriever = EmbeddingRetriever(document_store=self.document_store,
                                                 embedding_model="deepset/sentence_bert")
        custom_retriever = CustomRetriever()
        self.question_generator = FurtherQuestionGenerator()
        self.document_store.update_embeddings(dpr_retriever)
        self.dpr_node = ContinualDPRNode(dpr_retriever, self.document_store)

        self.trainer = DPRTrainingManager(self.document_store, self.dpr_node)
        self.pipeline = Pipeline()
        self.pipeline.add_node(component=es_retriever,
                               name="ESRetriever", inputs=["Query"])
        self.pipeline.add_node(component=self.dpr_node,
                               name="DPRRetriever", inputs=["Query"])
        self.pipeline.add_node(component=embedding_retriever,
                               name="EmbeddingRetriever", inputs=["Query"])
        self.pipeline.add_node(component=custom_retriever,
                               name="CustomRetriever", inputs=["Query"])
        self.pipeline.add_node(component=JoinDocuments(join_mode="merge"), name="JoinResults", inputs=[
            "ESRetriever", "DPRRetriever", "EmbeddingRetriever", "CustomRetriever"])
        self.pipeline.add_node(component=self.question_generator,
                               name="QnGenerator", inputs=["JoinResults"])

    def answer(self, question, history={}):
        if self.pipeline is None:
            return ""

        print(f"USING HISTORY: {history}")
        self.question_generator.history = history
        responses = self.pipeline.run(
            query=question, top_k_retriever=5)
        return responses[0].text

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
