from .KeyInfoExtractor import KeywordExtractor
from .parsing import Parser
from .pressure_score_generator import PressureScoreGenerator
from threading import RLock


class ResponseRequiredException(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class FurtherQuestionGenerator:
    outgoing_edges = 1

    def __init__(self):
        self.history = {}
        self.parser = Parser()
        self.setup_keyword_extractor()
        self.pressure_score_generator = PressureScoreGenerator()
        self.update_lock = RLock()

    def setup_keyword_extractor(self):
        key_word_extractor = KeywordExtractor()
        key_word_extractor.read_key_info_file("knowledgeBase/categories.csv")
        key_word_extractor.check_current_categories(True)
        questions = {}
        for ki in key_word_extractor.key_infos:
            questions[ki.name] = ki.question
        self.key_word_extractor = key_word_extractor
        self.questions = questions

    def question_parsing(self, text):
        parsed = self.parser.parse(text)
        parsed_string = ""
        for string in parsed["simple"]:
            parsed_string = parsed_string + string
        parsed_string = re.sub("[\(\[].*?[\)\]]", "", parsed_string)
        parsed_string = re.sub("  ", " ", parsed_string)
        return parsed_string

    def generate_keywords(self, text):
        parsed = self.parser.parse(text)
        parsed_string = ""
        for string in parsed["simple"]:
            parsed_string = parsed_string + string
        keywords = {}
        while (parsed_string.find("(") != -1):
            start = parsed_string.find("(")
            end = parsed_string.find(")")
            bracket = parsed_string[start + 1:end]
            if bracket.find(":") != -1:
                colon = bracket.find(":")
                keywords[bracket[1:colon].replace(
                    " ", "")] = bracket[colon + 1:].replace(" ", "")
            parsed_string = parsed_string[end + 1:]
        return keywords

    def individualFiltersGenerator(self, text):
        text = text.lower()
        keywords = self.key_word_extractor.get_best_matches(text)
        # print(current_filters)
        #print(key_word_extractor.get_best_matches(text.lower(), give_list=True))

        # The extraction of pressure keywords work differently from others
        if text.find("pressure") != -1:
            keywords["pressure"] = []
            if "low" in text[text.find("pressure") - 20:text.find("pressure") + 30]:
                keywords["pressure"].append("low")
            if "moderate" in text[text.find("pressure") - 20:text.find("pressure") + 30]:
                keywords["pressure"].append("moderate")
            if "high" in text[text.find("pressure") - 20:text.find("pressure") + 30]:
                keywords["pressure"].append("high")
            if "very high" in text[text.lower().find("pressure") - 20:text.lower().find("pressure") + 30] or "extreme" in text[text.find("pressure") - 20:text.find("pressure") + 30]:
                keywords["pressure"].append("very high")

        # To include special keywords such as variety
        parsed_keywords = self.generate_keywords(text)
        if parsed_keywords != {}:
            for key, value in parsed_keywords.items():
                if key not in keywords:
                    keywords[key] = [value]
                else:
                    keywords[key].append(value)
        return keywords

    def topDocsFilterGenerator(self, docs):
        return [self.individualFiltersGenerator(doc.text) for doc in docs]

    def filters_difference(self, filters_list, specified=[]):
        current_filters = {}
        for filters in filters_list:
            for category, filters in filters.items():
                if ((category not in specified) and (category in current_filters) and (filters != current_filters[category])):
                    return category
                elif ((category not in specified) and (category not in current_filters)):
                    current_filters[category] = filters
        return None

    def furtherQuestions(self, docs, specified=[], original_filters={}):
        filters_list = self.topDocsFilterGenerator(docs)
        # print(len(docs),len(filters_list))

        # Filter the retrieved docs before asking questions, eliminate docs with different keywords but keep those does not mention the keywords.
        if original_filters:
            for keyword, new_key in original_filters.items():
                temp_d = [doc for i, doc in enumerate(docs) if not (
                    (keyword in filters_list[i].keys()) and (new_key[0].lower() not in filters_list[i][keyword]))]
                temp_f = [filters for i, filters in enumerate(filters_list) if not (
                    (keyword in filters_list[i].keys()) and (new_key[0].lower() not in filters_list[i][keyword]))]
            docs = temp_d
            filters_list = temp_f
        # print(len(docs),len(filters_list))

        # Rank the docs based on closeness to keywords in question
        match = [0 for doc in docs]
        for keyword, new_key in original_filters.items():
            match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (new_key[0].lower(
            ) in filters_list[i][keyword])) else match[i] for i in range(len(filters_list))]
            match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (filters_list[i][keyword] == [
                                      new_key[0].lower()])) else match[i] for i in range(len(filters_list))]

        # Use only questions from the top 3 results. Otherwise too many questions asked.
        docs = [x for _, x in sorted(
            zip(match, docs), key=lambda pair: pair[0], reverse=True)]
        filters_list = [x for _, x in sorted(
            zip(match, filters_list), key=lambda pair: pair[0], reverse=True)]
        keyword = self.filters_difference(filters_list[:3], specified)
        contained_pressure = False
        while keyword is not None:
            if keyword != "pressure":
                new_key = None
                q = self.questions[keyword] + "(If not, please reply No) "
                if (q in self.history):
                    new_key = self.history[q]
                else:
                    raise ResponseRequiredException(q)
                if (new_key.lower() != "no"):
                    match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (new_key.lower(
                    ) in filters_list[i][keyword])) else match[i] for i in range(len(filters_list))]
                    match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (filters_list[i][keyword] == [
                                              new_key.lower()])) else match[i] for i in range(len(filters_list))]
                specified.append(keyword)
                original_filters[keyword] = [new_key]
            else:
                contained_pressure = True
                specified.append(keyword)
                original_filters[keyword] = []
            keyword = self.filters_difference(filters_list[:3], specified)

        # Treat the special set of pressure score questions
        if contained_pressure and "Crop" in original_filters:
            pressure_level = self.pressure_score_generator.calculate_pressure_score(
                original_filters["Crop"][0])
            match = [match[i] + 1 if (("pressure" in filters_list[i].keys()) and (
                pressure_level in filters_list[i]["pressure"])) else match[i] for i in range(len(filters_list))]
            match = [match[i] + 1 if (("pressure" in filters_list[i].keys()) and (
                filters_list[i]["pressure"] == [pressure_level])) else match[i] for i in range(len(filters_list))]
        sorted_docs = sorted(
            zip(match, docs), key=lambda pair: pair[0], reverse=True)
        # for doc in sorted_docs:
        # print(doc[1].text)
        # print(doc[1].meta)
        return sorted_docs[:3]

    def run(self, **kwargs):
        with self.update_lock:
            #print("Running Question Generator")
            original_filters = self.individualFiltersGenerator(kwargs["query"])
            specified = list(original_filters.keys())
            return ({"result": self.furtherQuestions(kwargs["documents"], specified, original_filters)}, "output_1")

    def update_components(self):
        with self.update_lock:
            self.setup_keyword_extractor()
            self.pressure_score_generator.update_pressure_table()
