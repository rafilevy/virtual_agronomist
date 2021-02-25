# import haystack
from haystack.retriever.dense import DensePassageRetriever
from DPRTrainingSet import DPRTrainingSet

class DPRTrainingManager:


# ##################
# constructor
#
# document store
#  - needed to find document text from
#  - currently uses the same one given
#  - could replace in future (e.g. input postgres address)
#
# startRetrieverVerson
#  - when training it improves on the most recent model
#  - as currently setup needs a model at /training/saved_models/dprX
#    (where X is the value passed in as startRetrieverVerson)
# ##################
    def __init__(self, documentStore, startRetrieverVerson):
        self.round = startRetrieverVerson+1
        self.trainingSet = DPRTrainingSet(documentStore,self.round)
        self.documentStore = documentStore


###################
# train a new model, and start working on future trainingSet
# returns path to new model
###################
    def train(self):

        #file where all the training stuff is
        doc_dir = "data/"
        #subdirectory of doc_dir where trainingsets arguments
        trainingDataLoc = "trainingSets/generated/"
        #directory where generated models are save_dir
        save_dir = "saved_models/"

        saveFileName = doc_dir + trainingDataLoc + str(self.round) + ".json"

        self.trainingSet.addInBatchNegatives()
        self.trainingSet.generateJSON(saveFileName)

        train_filename = trainingDataLoc + str(self.round) + ".json"
        dev_filename = "trainingSets/validationSet.json"
        save_dir = "saved_models/dpr" + str(self.trainingSet.round)

        old_modelDir = "saved_models/dpr" + str(self.trainingSet.round-1)

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
        return save_dir

##################
# adds an item to the training set
#
# question: string
# posID: document store ID
# negIDS: list of document store IDs
##################
    def addItem(self,question,posID,negIDs):
        self.trainingSet.addItem(question, posID, negIDs)

#################
# returns the current in memory training set size
# can query to work out whether to run training yet
#################
    def getNextSetSize(self):
        return len(self.trainingSet.trainingSet)
