# import haystack
from haystack.document_store.faiss import FAISSDocumentStore
from haystack.file_converter.txt import TextConverter
from haystack.preprocessor.preprocessor import PreProcessor
from haystack.retriever.dense import DensePassageRetriever
from training.DPRTrainingSet import DPRTrainingSet


class DPRTrainingTester:
    """
    To run with an in memory sqlite database
    """
    document_store = FAISSDocumentStore(
        faiss_index_factory_str="Flat"
    )

    retreiver = DensePassageRetriever(
        document_store=document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
        max_seq_len_query=64,
        max_seq_len_passage=256,
        batch_size=16,
        # use_gpu=True,
        use_gpu=False,
        embed_title=True,
        use_fast_tokenizers=True
    )

    # Loads the test document into the document store
    def loadDocumentsFromFile(self, knowledgeFilePath):
        converter = TextConverter(
            remove_numeric_tables=False,
            valid_languages=["en"])
        processor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=False,
            clean_header_footer=True,
            split_by="passage",
            split_length=1,
            split_respect_sentence_boundary=False,
            split_overlap=0
        )
        self.trainingFile = knowledgeFilePath
        loadedFile = converter.convert(knowledgeFilePath)
        documents = processor.process(loadedFile)
        for i in range(0, len(documents)):
            docMetadata = documents[i]['meta']
            docMetadata['name'] = knowledgeFilePath
            docMetadata['doucmentID'] = knowledgeFilePath \
                + str(docMetadata['_split_id'])

        self.document_store.write_documents(documents)
        backagain = self.document_store.get_all_documents()

        print("Number of documents loaded", end=": ")
        print(self.document_store.get_document_count())

    def __init__(self, knowledgeFilePath):
        print("Started DPR Training tester!")

        # load test document into database
        print("Loading documents from " + knowledgeFilePath)
        self.document_store.delete_all_documents()
        self.loadDocumentsFromFile(knowledgeFilePath)

        # update dpr embeddings based on initial retreiver
        print("Performing initial embeddings update")
        self.document_store.update_embeddings(self.retreiver)

        # generate a new dprTrainingSet to populate
        self.trainingSet = DPRTrainingSet(self.document_store, 0)

    # return document store's id for the response marked correct
    def get_correct_id(self, responses, correctNum):
        # correctRespons = responses[correctNum].to_dict()
        return responses[correctNum].id

    # return list of document store ids for alternative responses
    def get_incorrect_ids(self, responses, correctNum):
        ids = []
        for i in range(0, len(responses)):
            if i == correctNum:
                continue
            ids.append(responses[i].id)
        return ids

    def askQuestion(self):
        print("------------------------------")
        question = input("Enter new question (DONE to finish): ")

        if question == "":
            return

        if question == 'DONE':
            self.generateTraining()
            return

        k = 10
        responses = self.retreiver.retrieve(question, top_k=k)

        print()
        for i in range(0, k):
            print(i, end=": ")
            print(responses[i].text)
            # print(responses[i])
            print()

        print()
        correctNum = input("Select correct response (X if none correct): ")

        if correctNum == "":
            return

        if correctNum == 'X':
            return

        print()
        print("------------------------------")

        self.trainingSet.addItem(
            question=question,
            posID=self.get_correct_id(responses, int(correctNum)),
            negIDs=self.get_incorrect_ids(responses, int(correctNum))
        )

    # file where all the training stuff is
    doc_dir = "data/"

    def generateTraining(self):
        self.trainingSet.addInBatchNegatives()

        self.trainingSet.generateJSON(self.trainingFile + "SET.json")
        print("New training set saved to: " + self.trainingFile + "SET.json")

        exit(0)

    def loop(self):
        self.askQuestion()


import sys

if len(sys.argv) != 2:
    print("USAGE: python DPRTrainingGenerator knowledgeFilePath")
    exit(1)

tester = DPRTrainingTester(sys.argv[1])
# tester = DPRTrainingTester("winterBarley.txt")
# tester.train()
while(True):
    tester.loop()
