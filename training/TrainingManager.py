# import haystack
from haystack.retriever.dense import DensePassageRetriever
from DPRTrainingSet import DPRTrainingSet
from os import walk


class DPRTrainingManager:

    @classmethod
    def get_current_round(cls):
        max_round = -1
        try:
            directory = "training/saved_models/"
            _, _, filenames = next(walk(directory))

            for filename in filenames:
                try:
                    cur_round = int(filename.replace("dpr", ""))
                    max_round = max(cur_round, max_round)
                except:
                    pass
        except:
            pass
        return max_round

    @classmethod
    def get_current_retriever(cls, document_store):
        max_round = cls.get_current_round()
        if max_round != -1:
            old_modelDir = f"training/saved_models/dpr{max_round}"

            return retreiver = DensePassageRetriever.load(
                document_store=documentStore,
                load_dir=old_modelDir,
                max_seq_len_query=64,
                max_seq_len_passage=256,
                batch_size=16,
                # use_gpu=True,
                use_gpu=False,
                embed_title=True,
                use_fast_tokenizers=True
            )

        return DensePassageRetriever(document_store=document_store,
                                     query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
                                     passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
                                     max_seq_len_query=64,
                                     max_seq_len_passage=256,
                                     batch_size=16,
                                     use_gpu=True,
                                     embed_title=True,
                                     use_fast_tokenizers=True)

    # ##################
    # constructor
    #
    # document store
    #  - needed to find document text from
    #  - currently uses the same one given
    #  - could replace in future (e.g. input postgres address)
    #
    # ##################
    def __init__(self, documentStore, dpr_node):
        self.dpr_node = dpr_node
        self.round = DPRTrainingManager.get_current_round() + 1
        self.trainingSet = DPRTrainingSet(documentStore, self.round)
        self.documentStore = documentStore
        self.current_responses = None

    ###################
    # train a new model, and start working on future trainingSet
    # returns path to new model
    ###################
    def train(self):

        # file where all the training stuff is
        doc_dir = "training/data/"
        # subdirectory of doc_dir where trainingsets arguments
        trainingDataLoc = "trainingSets/generated/"

        saveFileName = doc_dir + trainingDataLoc + str(self.round) + ".json"

        self.trainingSet.addInBatchNegatives()
        self.trainingSet.generateJSON(saveFileName)

        train_filename = trainingDataLoc + str(self.round) + ".json"
        dev_filename = "trainingSets/validationSet.json"
        save_dir = "training/saved_models/dpr" + str(self.trainingSet.round)

        old_modelDir = "training/saved_models/dpr" + \
            str(self.trainingSet.round - 1)

        retreiver = DensePassageRetriever.load(
            document_store=self.documentStore,
            load_dir=old_modelDir,
            max_seq_len_query=64,
            max_seq_len_passage=256,
            batch_size=16,
            # use_gpu=True,
            use_gpu=False,
            embed_title=True,
            use_fast_tokenizers=True
        )

        retreiver.train(
            data_dir=doc_dir,
            train_filename=train_filename,
            dev_filename=dev_filename,
            test_filename=dev_filename,
            n_epochs=1,
            batch_size=4,
            # batch_size=1,
            grad_acc_steps=4,
            save_dir=save_dir,
            evaluate_every=3000,
            # evaluate_every=1,
            embed_title=True,
            num_positives=1,
            num_hard_negatives=1
        )

        self.round += 1
        self.trainingSet = DPRTrainingSet(self.documentStore, self.round)
        self.dpr_node.update_retriever(retreiver)

    ##################
    # adds an item to the training set
    #
    # question: string
    # posID: document store ID
    # negIDS: list of document store IDs
    ##################
    def addItem(self, question, posID, negIDs):
        self.trainingSet.addItem(question, posID, negIDs)

    #################
    # returns the current in memory training set size
    # can query to work out whether to run training yet
    #################
    def getNextSetSize(self):
        return len(self.trainingSet.trainingSet)

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

    def processQuestion(self, question):
        if self.current_responses is not None:
            return []

        k = 5
        retreiver = self.dpr_node.retriever
        self.current_responses = retreiver.retrieve(question, top_k=k)

        return [x.text for x in self.current_responses] + ["None of above"]

    def processTrainingAction(self, question, correct_text):
        if correct_text != "None of above":
            try:
                correct_num = [x.text for x in self.current_responses].index(
                    correct_text)
                self.trainingSet.addItem(
                    question=question,
                    posID=self.get_correct_id(
                        self.current_responses, int(correct_num)),
                    negIDs=self.get_incorrect_ids(
                        self.current_responses, int(correct_num))
                )
            except:
                pass
        self.current_responses = None
