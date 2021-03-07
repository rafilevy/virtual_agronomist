# import haystack
from haystack.retriever.dense import DensePassageRetriever
from training.DPRTrainingSet import DPRTrainingSet
from os import walk
import json
import _thread
from threading import Lock


class DPRTrainingManager:

    @classmethod
    def get_current_round(cls):
        max_round = -1
        try:
            directory = "training/saved_models/"
            _, directories, _ = next(walk(directory))

            for directory in directories:
                try:
                    cur_round = int(directory.replace("dpr", ""))
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
            return DensePassageRetriever.load(
                document_store=document_store,
                load_dir=old_modelDir,
                max_seq_len_query=64,
                max_seq_len_passage=256,
                batch_size=16,
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
                                     use_gpu=False,
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
        self.training = False
        self.training_lock = Lock()
        self.dpr_node = dpr_node
        self.round = DPRTrainingManager.get_current_round() + 1
        self.documentStore = documentStore
        self.current_responses = None

    ###################
    # train a new model, and start working on future trainingSet
    # returns path to new model
    ###################
    def train(self, objs):
        if self.training:
            return

        trainingSet = DPRTrainingSet(self.documentStore, self.round)
        for pretrain_object in objs:
            user_data = json.loads(pretrain_object.user_data)
            meta_data = json.loads(pretrain_object.meta_data)
            correct_num = user_data["choice"]
            print(user_data)
            print(meta_data)
            print(correct_num)
            if correct_num < len(meta_data):
                try:
                    trainingSet.addItem(
                        question=user_data["question"],
                        posID=self.get_correct_id(meta_data, correct_num),
                        negIDs=self.get_incorrect_ids(meta_data, correct_num)
                    )
                    print("ADDED TO TRAININGSET")
                except Exception as e:
                    print(user_data)
                    print(meta_data)
                    print(str(e))
                    pass

        objs.delete()
        with self.training_lock:
            self.training = True
        _thread.start_new_thread(self._train, (trainingSet, ))

    def _train(self, trainingSet):
        assert len(trainingSet.trainingSet) > 0
        # file where all the training stuff is
        doc_dir = "training/data/"
        # subdirectory of doc_dir where trainingsets arguments
        trainingDataLoc = "trainingSets/generated/"

        trainSaveFileName = doc_dir + trainingDataLoc + str(self.round) + ".json"
        devSaveFileNames = doc_dir + trainingDataLoc + str(self.round) + "DEV.json"

        trainingSet.addInBatchNegatives()
        trainingSet.generateJSON(trainSaveFileName,devSaveFileNames)

        train_filename = trainingDataLoc + str(self.round) + ".json"
        dev_filename = trainingDataLoc + str(self.round) + "DEV.json"
        test_filename = "trainingSets/validationSet.json"
        save_dir = "training/saved_models/dpr" + str(trainingSet.round)

        retreiver = DPRTrainingManager.get_current_retriever(
            self.documentStore)

        retreiver.train(
            data_dir=doc_dir,
            train_filename=train_filename,
            dev_filename=dev_filename,
            test_filename=test_filename,
            n_epochs=1,
            batch_size=1,
            grad_acc_steps=16,
            save_dir=save_dir,
            evaluate_every=1000,
            embed_title=True,
            num_positives=1,
            num_hard_negatives=1
        )

        self.round += 1
        self.dpr_node.update_retriever(
            DPRTrainingManager.get_current_retriever(self.documentStore))
        with self.training_lock:
            self.training = False

    # return document store's id for the response marked correct
    def get_correct_id(self, responses, correctNum):
        # correctRespons = responses[correctNum].to_dict()
        return responses[correctNum]['id']

    # return list of document store ids for alternative responses
    def get_incorrect_ids(self, responses, correctNum):
        ids = []
        for i in range(0, len(responses)):
            if i == correctNum:
                continue
            ids.append(responses[i]['id'])
        return ids

    def processQuestion(self, question):
        k = 5
        retreiver = self.dpr_node.retriever
        current_responses = retreiver.retrieve(question, top_k=k)

        return current_responses
        # return [x.text for x in self.current_responses] + ["None of above"]

    def processTrainingAction(self, question, choices, correct_num):
        if correct_num < len(choices):
            user_data = {
                "question": question,
                "options": [x.text for x in choices],
                "choice": correct_num,
            }
            meta_data = [{"text": x.text, "id": x.id}
                         for x in choices]
            return {"user_data": json.dumps(user_data), "meta_data": json.dumps(meta_data)}
        return None

    def getCorrectDict(self, question, answer):
        user_data = {
            "question": question,
            "options": [answer.text],
            "choice": 0,
        }
        meta_data = [{"text": answer.text, "id": answer.id}]
        return {"user_data": json.dumps(user_data), "meta_data": json.dumps(meta_data)}
