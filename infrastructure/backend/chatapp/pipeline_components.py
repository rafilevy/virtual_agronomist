from threading import RLock
from transformers import AutoTokenizer, AutoModelForTableQuestionAnswering, TableQuestionAnsweringPipeline


class Result:
    outgoing_edges = 1

    def run(self, **kwargs):
        # print("Running Result")
        # print(type(kwargs["result"]))
        if type(kwargs["result"]) is list:
            #docs = [doc[1] for doc in kwargs["result"]]
            return (kwargs["result"], "output_1")
        else:
            return (kwargs["result"]["answer"], "output_1")


class QueryClassifier:
    outgoing_edges = 2

    def run(self, **kwargs):
        # print("Running Query Classifier")
        # print(len(kwargs["documents"]))
        # print(kwargs["documents"][0].meta)
        # for doc in kwargs["documents"]:
        #  print(doc.text)
        # print(kwargs["documents"][0].meta["table"] == "0")
        # docs = kwargs["documents"]
        if (kwargs["documents"][0].meta["table"] == "false"):
            # print("It is a general question.")
            return (kwargs, "output_1")
        else:
            # print("It is a table-related question.")
            return (kwargs, "output_2")


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


class TableRetriever:
    outgoing_edges = 1

    def __init__(self, table_data):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "google/tapas-base-finetuned-wtq")
        self.model = AutoModelForTableQuestionAnswering.from_pretrained(
            "google/tapas-base-finetuned-wtq")
        self.tableQA = TableQuestionAnsweringPipeline(
            model=self.model, tokenizer=self.tokenizer)
        self.data = table_data

    def run(self, **kwargs):
        # print("Running Table Retriever")

        # print("Finished")
        print(kwargs["documents"][0].meta)
        return ({"result": self.tableQA(self.data[int(kwargs["documents"][0].meta["index"])], kwargs["query"])}, "output_1")
