# Training Overview

Training is possible for the Retriever part of the pipeline - the model used is outlined in a paper by [Karpukhin et al. 2020](https://arxiv.org/abs/2004.04906).

When users report questions they get added to a database table called PreTrainingData - which records the answer they chose and the other answers that the system predicted the user may want.

On the training tab of the admin page - the admin can go through all these reports to create a training set which then triggers a training session. Once training is complete the pipeline starts using the new model - so any questions sent after this point use the new retriever.

## DPRTrainingSet.py
`infrastructure/backend/training/DPRTrainingSet.py` 

This file handles the generation of the JSON training files that are used for training.

It defines the class `DPRTrainingItem` which handles all the information for a single training point. It also defines the class `DPRTrainingSet` which keeps a list of `DPRTrainingItem` objects that can be manipulated with the methods `addItem`, `addInBatchNegatives` and `generateJSON`.

- `addItem(string question,string posID,string[] negIDs)`: given a question and the Documents Store ID for the correct answer and a list of IDs for negative answers. Together these form the information stored in one datapoint
- `addInBatchNegatives()`: adds extra negative contexts to every point. It does this by adding the positive answers from other questions in the training batch as negative answers. (This is recommended in the paper linked above)
- `generateJSON(string: trainingFileName, string: devFileName)`: reserves some of the training set to become a development set (not used in training but used to evaluate the success of the training) and produces two files in the JSON form that Haystack expects.

## TrainingManager.py
`infrastructure/backend/training/TrainingManager.py`

This defines the `TrainingManager` class which is used to manage the actual training.

- `get_current_round()` this returns the version number of the most recently trained model
`get_current_retriever()` this loads the most recent model
- `train(objs)`: this takes in the objects from the `PreTrainingData` store and adds the ones reviewed by an admin to a `DPRTrainingSet` object. It then triggers the actual training code (in a new thread)
- `processQuestion(string: question)`: this returns the top few answers using just the DPR retriever (as if the pipeline contains just this)
- `processTrainingAction(string: question, string[] choices, int: correct_num)`: returns the object to add to the `PreTrainingData` store when the user reports a question.
