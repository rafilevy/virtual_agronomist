import nltk
from typing import List

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

#  testQuestionEmpty = ""
#  testQuestionBland = "This has no keywords in it"
#  testQuestion = "Does winter barley need treating for Ramularia at T1?"
#  testQuestion2 = "Do winter barley winter oilseed rape spring oats need treating for Ramularia at T1?"
#  testQuestion3 = "Do winter barley or winter oilseed rape spring oats need treating for Ramularia at T1?"
#  testQuestion4 = "Do I need to spray my winter beans at mid flower or t2?"
#  testQuestionStress = "Do winter barley winter barley or oilseed rape or spring oats need YEET treating for Ramularia or Phoma Stem Canker at T1?"
#  testQuestionStress2 = "winter winter barley barley"
#  testQuestionStress3 = "winter barley spring oilseed rape winter oilseed rape"
#  testQuestionWithEverything = "Should i apply standon beamer to my winter barley at t0 if there is evidence of ramularia"


class KeywordExtractor:
    def __init__(self):
        self.key_infos = []
        print("1* Made an Extractor")

    class KeyInfo:
        #  class that allows to expand to other keywords/categories
        #  need to give category name, one grams and two grams
        def __init__(self, name, one_grams, completes):
            self.name = name
            self.one_grams = one_grams
            self.completes = completes

    def merge_dicts(self, dict1, dict2):
        if dict2 is None:
            return dict1
        for key in dict2:
            if key in dict1:
                dict1[key] = dict1[key] + dict2[key]
            else:
                dict1[key] = dict2[key]
        return dict1

    def check_current_categories(self, verbose=False):
        print("Currently held Categories: ")
        if verbose:
            for ki in self.key_infos:
                print("* ", ki.name + ": ", ki.one_grams, " || ", ki.completes)
        else:
            for ki in self.key_infos:
                print("* ", ki.name)
        print()

    def add_key_info_category(self, key_info):
        self.key_infos.append(key_info)

    def add_key_info_categories(self, key_is):
        for ki in key_is:
            self.key_infos.append(ki)

    def read_key_info_file(self, filename, category_name):
        import csv

        csv.register_dialect('csv_dialect', skipinitialspace=True)

        with open(f"keywordExtractor/{filename}") as f:
            reader = csv.reader(f, dialect='csv_dialect')
            data = list(reader)[0]

        set_data = set()
        for w in data:
            set_data.add(w)

        completes = list(set_data)
        one_grams = set({})

        for d in data:
            words = nltk.word_tokenize(d)
            for w in words:
                one_grams.add(w)

        one_grams_l = list(one_grams)

        key_info = self.KeyInfo(category_name, one_grams_l, completes)
        self.add_key_info_category(key_info)

        return key_info

    def read_key_info_files(self, filenames, category_names):
        if len(filenames) != len(category_names):
            print("Lists of unequal length, cannot add categories")
            return
        kis = []
        for i in range(len(filenames)):
            ki = self.read_key_info_file(filenames[i], category_names[i])
            kis.append(ki)

        return kis

    def standardise_format(self, phrase):
        print("2* INPUT: " + phrase)
        lowered_phrase = phrase.lower()
        one_grams = nltk.word_tokenize(lowered_phrase)
        return one_grams

    def get_best_matches(self, phrase, give_list=True):
        tokens = self.standardise_format(phrase)
        best_matches = {}
        for key_info in self.key_infos:
            d = self.make_dict(tokens, key_info.one_grams, key_info.completes)
            best = self.get_best_match(d, give_list)
            if best is not None:
                best_matches[key_info.name] = best

        # make list of objects - name, 1 grams, completes to allow update
        print("3* OUTPUT: ", best_matches)
        return best_matches

    def get_best_match(self, diction, give_list):
        if diction:
            max_count = 0
            possible_keys = []
            for key in diction:
                if diction[key] > max_count:
                    max_count = diction[key]
                    possible_keys = [key]
                elif diction[key] == max_count:
                    possible_keys.append(key)

            max_words = 0
            best_keys = []
            if len(possible_keys) > 0:
                for i in range(len(possible_keys)):
                    words = 1 + possible_keys[i].count(' ')
                    if words > max_words:
                        max_words = words
                        best_keys = [possible_keys[i]]
                    elif words == max_words:
                        best_keys.append(possible_keys[i])

            if give_list:
                return best_keys
            else:
                return best_keys[0]  # need to pick longest one!

    def make_dict(self, one_grams, target_one_grams, target_completes):
        building = False
        built = 0  # current length of run that we are building
        buffer = []
        diction = {}
        for i in range(len(one_grams)):
            if building:
                if one_grams[i] in target_one_grams:
                    built = built + 1
                    buffer.append(one_grams[i])
                else:
                    building = False
                    values = self.reduce_run(buffer, target_completes)
                    self.merge_dicts(diction, values)
                    built = 0
                    buffer = []
            else:
                if one_grams[i] in target_one_grams:
                    building = True
                    built = built + 1
                    buffer = [one_grams[i]]

        if building:
            values = self.reduce_run(buffer, target_completes)
            self.merge_dicts(diction, values)

        return diction

    def reduce_run(self, run, completes):
        n = len(run)
        diction = {}
        for len_of_run in range(n, 0, -1):
            for start_index in range(0, n - len_of_run + 1):
                var = ' '.join(run[start_index:start_index + len_of_run])
                if var in completes:
                    if var in diction:
                        diction[var] = diction[var] + 1
                    else:
                        diction[var] = 1
                    if len_of_run != n:
                        # separator needed
                        reduced_run = run[0:start_index] + \
                            ["*"] + run[start_index + len_of_run:n]
                        d = self.reduce_run(reduced_run, completes)
                        self.merge_dicts(diction, d)
                    return diction


shared_extractor = KeywordExtractor()
shared_extractor.read_key_info_files(
    ["disease.csv", "crop.csv", "fungicide.csv", "timing.csv"],
    ["Disease", "Crop", "Fungicide", "Timing"]
)
