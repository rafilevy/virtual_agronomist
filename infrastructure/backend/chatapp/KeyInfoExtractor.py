import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class KeywordExtractor:
    def __init__(self):
        self.key_infos = []
        #print("1* Made an Extractor")

    class KeyInfo:
        #  class that allows to expand to other keywords/categories
        #  need to give category name, one grams and two grams
        def __init__(self, name, one_grams, completes, question):
            self.name = name
            self.one_grams = one_grams
            self.completes = completes
            self.question = question

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
                print("* ", ki.name + ": " + ki.question + " ", ki.completes)
        else:
            for ki in self.key_infos:
                print("* ", ki.name)
        print()

    def add_key_info_category(self, key_info):
        self.key_infos.append(key_info)

    def add_key_info_categories(self, key_is):
        for ki in key_is:
            self.key_infos.append(ki)

    def read_key_info_file(self, filename, verbose=False):
        self.key_infos = []  # reset ?

        import csv
        csv.register_dialect('csv_dialect', skipinitialspace=True)

        #  format of csv is Category| Question| keyword| keyword.....
        #  need to change to be delimited by |? so that questions can contain commas?

        with open(filename) as f:
            reader = csv.reader(f, dialect='csv_dialect', delimiter='|')  # delimiter='|' ?
            data = list(reader)
            lines = len(data)

        for line in data:
            cat = line[0].lower()
            que = line[1]
            values = line[2:]

            set_data = set()
            for ws in values:
                set_data.add(ws.lower())

            completes = list(set_data)

            if verbose:
                print("Category: ", cat, "\nQuestion: ", que, "\nValues: ", completes)

            one_grams = set({})
            for value in values:
                words = nltk.word_tokenize(value)
                for w in words:
                    one_grams.add(w)

            one_grams_l = list(one_grams)

            key_info = self.KeyInfo(cat, one_grams_l, completes, que)
            self.add_key_info_category(key_info)

    def standardise_format(self, phrase):
        #print("2* INPUT: " + phrase)
        lowered_phrase = phrase.lower()
        one_grams = nltk.word_tokenize(lowered_phrase)
        return one_grams

    def get_best_matches(self, phrase):
        tokens = self.standardise_format(phrase)
        best_matches = {}
        for key_info in self.key_infos:
            d = self.make_dict(tokens, key_info.one_grams, key_info.completes)
            best = self.get_best_match(d)
            if best is not None:
                best_matches[key_info.name] = best

        # make list of objects - name, 1 grams, completes to allow update
        #print("3* OUTPUT: ", best_matches)
        return best_matches

    def get_best_match(self, diction):
        if diction:
            possible_keys = []
            for key in diction:
                possible_keys.append(key)
            return possible_keys

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
                        reduced_run = run[0:start_index] + ["*"] + run[start_index + len_of_run:n]  # separator needed
                        d = self.reduce_run(reduced_run, completes)
                        self.merge_dicts(diction, d)
                    return diction

