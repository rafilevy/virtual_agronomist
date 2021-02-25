Components of the system

-  Document store with certain properties
  - passages have "title" field
    - e.g "Winter Barley Fungicide"
  - passages have unique identifier
    - needed for DPR training

- Feedback data input
  - question asked
  - yes / no
  - given passage unique identifier
  - other retreived passages unique identifiers

- Find the correct answer
  - give user the other retreived passsage and select correct one?
  - Log for manual intervention

- DPR training data generator
  - in following form if was a "yes"
    - dataset = training round number
    - question = question asked
    - answers = passage given if report is yes
    - positive_ctxs = """"
    - negative_ctxs = []
    - hard_negative_ctxs = other retreived passages
                        + other positive_ctxs in training round

 - Annotation tool for better training???
