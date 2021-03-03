import csv
import re


class ChoiceRequiredException(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class PressureScoreGenerator:
    def __init__(self):
        self.pressure_table = {}
        self.update_pressure_table()

    def update_pressure_table(self):
        self.pressure_table = {}
        with open('knowledgeBase/pressure_score.csv', mode='r') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if row[0] in self.pressure_table:
                    if row[1] in self.pressure_table[row[0]]:
                        self.pressure_table[row[0]][row[1]][len(
                            self.pressure_table[row[0]][row[1]]) + 1] = [row[2], int(row[3])]
                    else:
                        self.pressure_table[row[0]][row[1]] = {
                            1: [row[2], int(row[3])]}
                else:
                    self.pressure_table[row[0]] = {
                        row[1]: {1: [row[2], int(row[3])]}}
        infile.close()

    def calculate_pressure_score(self, crop, history):
        if crop in self.pressure_table:
            score = 0
            print(history)
            # Would it be possible to change this into options by click?

            for key in self.pressure_table[crop].keys():
                message = "Please choose the " + key + \
                    " which best describes your current case:\n\n"
                print("Please choose the " + key +
                      " which best describes your current case: ")
                for option in self.pressure_table[crop][key]:
                    message = message + \
                        str(option) + ": " + \
                        self.pressure_table[crop][key][option][0] + "\n\n"
                if message in history and history[message].isnumeric() and (int(history[message]) >= 1 and int(history[message]) <= len(self.pressure_table[crop][key])):
                    score = score + \
                        self.pressure_table[crop][key][int(
                            history[message])][1]
                elif message in history:
                    message = "Your input is not Valid. Please refresh and try again."
                    raise ChoiceRequiredException(message)
                else:
                    raise ChoiceRequiredException(message)

            if score <= 12:
                pressure_level = "low"
            elif score <= 15:
                pressure_level = "moderate"
            elif score <= 18:
                pressure_level = "high"
            else:
                pressure_level = "very high"
            text = "Your current disease pressure score is " + \
                str(score) + ".\nThis means that the disease pressure is " + \
                pressure_level + "."
            print("Your current disease pressure score is " + str(score) +
                  ".\nThis means that the disease pressure is " + pressure_level + ".")
            return (pressure_level, text)
        else:
            return -1
