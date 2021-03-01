import csv
import re


class PressureScoreGenerator:
    def __init__(self):
        self.pressure_table = {}
        self.update_pressure_table()

    def update_pressure_table(self):
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

    def calculate_pressure_score(self, crop):
        if crop in self.pressure_table:
            print("To give a better suggestion. We need to calculate the disease pressure of your current case. Please specify your choice by replying with the number accordingly.")
            score = 0
            # Would it be possible to change this into options by click?
            for key in self.pressure_table[crop].keys():
                print("Please choose the " + key +
                      " which best describes your current case: ")
                for option in self.pressure_table[crop][key]:
                    print(option, ": ",
                          self.pressure_table[crop][key][option][0])
                choice = input()
                while not choice.isnumeric() or not (int(choice) >= 1 and int(choice) <= len(self.pressure_table[crop][key])):
                    choice = input(
                        "Your input is not Valid. Please check and try again.")
                score = score + self.pressure_table[crop][key][int(choice)][1]
            if score <= 12:
                pressure_level = "low"
            elif score <= 15:
                pressure_level = "moderate"
            elif score <= 18:
                pressure_level = "high"
            else:
                pressure_level = "very high"
            print("Your current disease pressure score is " + str(score) +
                  ".\nThis means that the disease pressure is " + pressure_level + ".")
            return pressure_level
        else:
            return -1
