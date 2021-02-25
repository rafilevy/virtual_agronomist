# #####################
# A brief intro
#
# To make a training set you need an instance of DPRTrainingSet
# how to use it:
#
#     constructor arguments
#        - a document store object
#         (one that connects to the same database as the pipeline)
#        - round number (e.g. 2 for 2nd training round)
#          (to ensure training sets saved to different file names)
#
#     addItem(question,posID, negIDs)
#         - question as a string
#         - id of document in document store (can be accessed by [document].id)
#         - negids is a LIST (posid is not a list)
#
#     addInBatchNegatives() and generateJSON(destination)
#         - used when making the JSON to dump
#         - call once then make a new DPRTraingSet object with new round number
#
# #############





import json # for outputting training dataset
import random # for adding in batch negatives

# the individidual data points to train
class DPRTrainingItem:

    # populate the data point with inital data
    def __init__(self,question,answer,positive_ctx,hard_negative_ctxs):
        self.dict_DPR = {
            "question": question,
            "answers": [answer],
            "positive_ctxs": [positive_ctx],
            "negative_ctxs": [],
            "hard_negative_ctxs": hard_negative_ctxs
        }

    # used to provide in batch negatives for other points
    def getPositiveCtx(self):
        return self.dict_DPR["positive_ctxs"][0]

    # add in batch negative from other points
    # return false if tried to add the positive context as a negative one
    def addNegativeCtx(self,c):
        if c["passage_id"]==self.getPositiveCtx()["passage_id"]:
            return False;
        else:
            self.dict_DPR["hard_negative_ctxs"].append(c)
            return True;

# contains set of dpr training items
# used to add training points and create json training file
class DPRTrainingSet:
    def __init__(self, document_store,round):
        self.document_store = document_store
        self.round = round
        self.trainingSet = []

    def getContext(self, id):
        document = self.document_store.get_document_by_id(id)
        context = {
            "title": "",
            "text": "",
            "score": 0,
            "title_score": None, #what on earth to with this....
            "passage_id": ""
        }
        context["title"] = document.meta['name']
        context["text"] = document.text
        context["score"] = document.score
        context["passage_id"] = document.id
        return context

    def addItem(self,question,posID,negIDs):
        # create dpr context from the id of the correct document
        positive_context = self.getContext(posID)#
        # extract the text as this is the correct answer
        answer = positive_context["text"]

        # create a list of all the contexts from incorrect documents
        negative_contexts = []
        for i in range(0,len(negIDs)):
            negative_contexts.append(self.getContext(negIDs[i]))

        newItem = DPRTrainingItem(
            question=question,
            answer=answer,
            positive_ctx=positive_context,
            hard_negative_ctxs=negative_contexts
        )
        self.trainingSet.append(newItem)
        return

    def addInBatchNegatives(self):
        # max number of negatives to add
        N = 10
        if N > len(self.trainingSet):
            N = len(self.trainingSet)

        for i in self.trainingSet:
            for j in range(0,N):
                neg = random.randint(0,len(self.trainingSet)-1)
                i.addNegativeCtx(self.trainingSet[neg].getPositiveCtx())

        # self.printSet()

    def generateJSON(self,saveFile):
        bigList = []
        for i in self.trainingSet:
            bigList.append(i.dict_DPR)

        items = [json.dumps(dataPoint, indent=6) for dataPoint in bigList]
        textOutput = "[%s]" % ",\n".join(items)
        open(saveFile,'w').write(textOutput)

    def printSet(self):
        for i in range(0,len(self.trainingSet)):
            print(self.trainingSet[i].dict_DPR)
            print()
