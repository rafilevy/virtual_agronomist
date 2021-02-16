import os
from subprocess import Popen, PIPE, STDOUT
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


class CustomRetriever(BaseRetriever):
    def retrieve(self, query, filters=None, top_k=10, index=None):
        super().retrieve(query, filters, top_k, index)
        # placeholder retriever
        return []


filters_dictionary = {"timings": ["t0", "t1", "t2", "t3"],
                      "fungus": ["ramularia", "rellow rust"],
                      "areas": ["east", "north", "southeast", "west", "south", "southwest"]}
questions = {"timings": "Is there a specific timing that you would like to ask about? (E.g. T0, T1, etc)",
             "fungus": "Is there a fungi type that you would want to know about specifically?",
             "area": "Which area are you in? (E.g. east, north, etc)"}


class FurtherQuestionGenerator:
    outgoing_edges = 1

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
            new_key = input(questions[keyword] + " ")
            match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (new_key.lower(
            ) in filters_list[i][keyword])) else match[i] for i in range(len(filters_list))]
            match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (filters_list[i][keyword] == [
                                      new_key.lower()])) else match[i] for i in range(len(filters_list))]
            specified.append(keyword)
            keyword = self.filters_difference(filters_list, specified)
        return [x for _, x in sorted(zip(match, docs), key=lambda pair: pair[0], reverse=True)]

    def run(self, **kwargs):
        specified = list(self.individualFiltersGenerator(
            kwargs["query"]).keys())
        return (self.furtherQuestions(kwargs["documents"], specified), "output_1")


class MLPipeline:
    def __init__(self):
        self.pipeline = None
        self.document_store = None

    def setup(self):
        print("SETTING UP PIPELINE")
        converter = haystack.file_converter.txt.TextConverter(
            remove_numeric_tables=False,
            valid_languages=["en"])

        as4 = converter.convert(
            file_path="../knowledgeBase/as4-winterBarley.txt")

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
        print("PROCESSED AS4 DOCS")
        self.document_store = ElasticsearchDocumentStore(
            similarity="dot_product", host="elasticsearch", username="", password="", index="document")
        # print("DELETED PREVIOUS DOCUMENTS")
        # self.document_store.delete_all_documents(index='document')
        self.document_store.write_documents(as4Docs)
        print("WRITTEN DOCUMENT")
        es_retriever = ElasticsearchRetriever(
            document_store=self.document_store)
        dpr_retriever = DensePassageRetriever(document_store=self.document_store,
                                              query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
                                              passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
                                              max_seq_len_query=64,
                                              max_seq_len_passage=256,
                                              batch_size=16,
                                              use_gpu=True,
                                              embed_title=True,
                                              use_fast_tokenizers=True)
        embedding_retriever = EmbeddingRetriever(document_store=self.document_store,
                                                 embedding_model="deepset/sentence_bert")
        custom_retriever = CustomRetriever()
        # question_generator = FurtherQuestionGenerator()

        self.document_store.update_embeddings(dpr_retriever)

        self.pipeline = Pipeline()
        self.pipeline.add_node(component=es_retriever,
                               name="ESRetriever", inputs=["Query"])
        self.pipeline.add_node(component=dpr_retriever,
                               name="DPRRetriever", inputs=["Query"])
        self.pipeline.add_node(component=embedding_retriever,
                               name="EmbeddingRetriever", inputs=["Query"])
        self.pipeline.add_node(component=custom_retriever,
                               name="CustomRetriever", inputs=["Query"])
        self.pipeline.add_node(component=JoinDocuments(join_mode="merge"), name="JoinResults", inputs=[
            "ESRetriever", "DPRRetriever", "EmbeddingRetriever", "CustomRetriever"])
        # self.pipeline.add_node(component=question_generator,
        #                        name="QnGenerator", inputs=["JoinResults"])

    def answer(self, question):
        if self.pipeline is None:
            return ""

        responses = self.pipeline.run(query=question, top_k_retriever=5)
        return responses['documents'][0].text


shared_pipeline = MLPipeline()
shared_pipeline.setup()
