# import haystack
from haystack.document_store.faiss import FAISSDocumentStore
from haystack.file_converter.txt import TextConverter
from haystack.preprocessor.preprocessor import PreProcessor
from haystack.retriever.dense import DensePassageRetriever
from DPRTrainingSet import DPRTrainingSet


class DPRTrainingTester:
    """
    To run with a seperate postgres database
    """
    # docker run  -p 5432:5432 -e POSTGRES_PASSWORD=haystack -d postgres
    # document_store = FAISSDocumentStore(
    #     faiss_index_factory_str="Flat",
    #     sql_url="postgresql://postgres:haystack@localhost:5432"
    # )

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
            clean_whitespace=True,
            clean_header_footer=True,
            split_by="passage",
            split_length=1,
            split_respect_sentence_boundary=False,
            split_overlap=0
        )
        loadedFile = converter.convert(knowledgeFilePath)
        documents = processor.process(loadedFile)
        for i in range(0, len(documents)):
            docMetadata = documents[i]['meta']
            docMetadata['name'] = knowledgeFilePath
            docMetadata['doucmentID'] = knowledgeFilePath \
                + str(docMetadata['_split_id'])

        self.document_store.write_documents(documents)
        backagain = self.document_store.get_all_documents()

        # for i in range(0,len(backagain)):
        #     print(i)
        #     print(":\n")
        #     print(backagain[i])
        #     print("---------------")

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
        question = input("Enter new question (T to run training): ")

        if question == 'T':
            self.train()
            return

        k = 5
        responses = self.retreiver.retrieve(question, top_k=k)

        print()
        for i in range(0, k):
            print(i, end=": ")
            print(responses[i].text)
            # print(responses[i])
            print()

        print()
        correctNum = input("Select correct response (X if none correct): ")

        if correctNum == 'X':
            return

        # print("Correct id: " + self.get_correct_id(responses,int(correctNum)))
        #
        # print("Incorrect ids: ", end = "")
        # incorrect = self.get_incorrect_ids(responses,int(correctNum))
        # for i in range (0,len(responses)-1):
        #     print(incorrect[i], end = " ")

        print()
        print("------------------------------")

        self.trainingSet.addItem(
            question=question,
            posID=self.get_correct_id(responses, int(correctNum)),
            negIDs=self.get_incorrect_ids(responses, int(correctNum))
        )
        # self.trainingSet.printSet()

    # file where all the training stuff is
    doc_dir = "data/"

    def train(self):
        self.trainingSet.addInBatchNegatives()

        trainingDataLoc = "trainingSets/generated/" \
            + str(self.trainingSet.round) \
            + ".json"

        self.trainingSet.generateJSON(self.doc_dir + trainingDataLoc)

        train_filename = trainingDataLoc

        dev_filename = "trainingSets/generated/validationSet.json"

        save_dir = "saved_models/dpr" + str(self.trainingSet.round)

        self.retreiver.train(
            data_dir=self.doc_dir,
            train_filename=train_filename,
            dev_filename=dev_filename,
            test_filename=dev_filename,
            n_epochs=1,
            # batch_size=4,
            batch_size=1,
            grad_acc_steps=4,
            save_dir=save_dir,
            # evaluate_every=3000,
            evaluate_every=1,
            embed_title=True,
            num_positives=1,
            num_hard_negatives=1
        )

        self.retreiver = DensePassageRetriever.load(
            document_store=self.document_store,
            load_dir=save_dir,
            max_seq_len_query=64,
            max_seq_len_passage=256,
            batch_size=16,
            # use_gpu=True,
            use_gpu=False,
            embed_title=True,
            use_fast_tokenizers=True
        )

        self.document_store.update_embeddings(self.retreiver)

        self.trainingSet = DPRTrainingSet(
            self.document_store,
            self.trainingSet.round + 1)

    def loop(self):
        self.askQuestion()


tester = DPRTrainingTester("winterBarley.txt")
# tester.train()
while(True):
    tester.loop()
