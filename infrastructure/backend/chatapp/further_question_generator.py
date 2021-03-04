from .KeyInfoExtractor import KeywordExtractor
from .TimingTranslator import TimingTranslator, TimingInfoCreator
from .parsing import Parser
from .pressure_score_generator import PressureScoreGenerator
from threading import RLock
import re


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
        self.setup_timing_translator()

    def setup_timing_translator(self):
        self.timing_info_creator = TimingInfoCreator({})
        self.timing_info_creator.read_csv_translate_table("knowledgeBase/translation.csv")
        self.timing_translator = TimingTranslator(self.timing_info_creator.crops_timing_data)

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
        keywords = self.key_word_extractor.get_best_matches(text)
        if "Crop" not in keywords and self.questions["Crop"] + "(If not, please reply No) " not in self.history:
            raise ResponseRequiredException(self.questions["Crop"] + "(If not, please reply No) ")
        elif "Crop" not in keywords:
            crop = self.history[self.questions["Crop"] + "(If not, please reply No) "]
        else:
            crop = keywords["Crop"][0]

        parsed = self.parser.parse(text)
        parsed_string = ""
        for string in parsed["simple"]:
            parsed_string = parsed_string + string
        parsed_string = re.sub("[\(\[].*?[\)\]]", "", parsed_string)
        parsed_string = re.sub("  ", " ", parsed_string)
        parsed_string = self.timing_translator.translate(parsed_string,crop)
        return crop + " " + parsed_string

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
            if " low " in text[text.find("pressure") - 20:text.find("pressure") + 30]:
                keywords["pressure"].append("low")
            if "moderate" in text[text.find("pressure") - 20:text.find("pressure") + 30]:
                keywords["pressure"].append("moderate")
            if " high " in text[text.find("pressure") - 20:text.find("pressure") + 30]:
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
        for doc in docs:
            print(type(doc))
            print(doc.meta)
            print(doc.meta["name"])
            
        return [self.individualFiltersGenerator(doc.meta["name"] + "  " + doc.text) for doc in docs]

    def filters_difference(self, filters_list, specified=[]):
        current_filters = {}
        print("\n\n",filters_list)
        for filters in filters_list:
            for category, filters in filters.items():
                if ((category not in specified) and (category in current_filters) and (filters != current_filters[category])):
                    return category
                elif ((category not in specified) and (category not in current_filters)):
                    current_filters[category] = filters
        print(current_filters,"\n\n")
        return None

    def furtherQuestions(self, docs, specified=[], original_filters={}):
        filters_list = self.topDocsFilterGenerator(docs)
        # print(len(docs),len(filters_list))

        # Filter the retrieved docs before asking questions, eliminate docs with different keywords but keep those does not mention the keywords.
        if original_filters:
            for keyword, new_key in original_filters.items():
                if len(new_key) > 0:
                    temp_d = [doc for i, doc in enumerate(docs) if not (
                    (keyword in filters_list[i].keys()) and (new_key[0].lower() not in filters_list[i][keyword]))]
                    temp_f = [filters for i, filters in enumerate(filters_list) if not (
                    (keyword in filters_list[i].keys()) and (new_key[0].lower() not in filters_list[i][keyword]))]
            docs = temp_d.copy()
            filters_list = temp_f.copy()
        # print(len(docs),len(filters_list))
        for pair in zip(docs,filters_list):
            print(pair[0].text)
            print(pair[1])

        # Rank the docs based on closeness to keywords in question
        match = [0 for doc in docs]
        for keyword, new_key in original_filters.items():
            if len(new_key) > 0:
                match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (new_key[0].lower(
            ) in filters_list[i][keyword])) else match[i] for i in range(len(filters_list))]
                match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (filters_list[i][keyword] == [
                                      new_key[0].lower()])) else match[i] for i in range(len(filters_list))]

        # Use only questions from the top 10 results. Otherwise too many questions asked.
        docs = [x for _, x in sorted(
            zip(match, docs), key=lambda pair: pair[0], reverse=True)]
        filters_list = [x for _, x in sorted(
            zip(match, filters_list), key=lambda pair: pair[0], reverse=True)]
        keyword = self.filters_difference(filters_list[:10], specified)
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
                    #temp_d = [doc for i, doc in enumerate(docs) if not ((keyword in filters_list[i].keys()) and (new_key.lower() not in filters_list[i][keyword]))]
                    #temp_f = [filters for i, filters in enumerate(filters_list) if not ((keyword in filters_list[i].keys()) and (new_key.lower() not in filters_list[i][keyword]))]
                    #temp_m = [mat for i, mat in enumerate(match) if not ((keyword in filters_list[i].keys()) and (new_key.lower() not in filters_list[i][keyword]))]

                    #doc = temp_d
                    #filters_list = temp_f
                    #match = temp_m

                    #print(len(doc),len(filters_list),len(match))
                    
                    match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (new_key.lower(
                    ) in filters_list[i][keyword])) else match[i] for i in range(len(filters_list))]
                    match = [match[i] + 1 if ((keyword in filters_list[i].keys()) and (filters_list[i][keyword] == [
                                              new_key.lower()])) else match[i] for i in range(len(filters_list))]

                    #temp_match = match.copy()
                    #temp_filters = sorted(zip(temp_match, filters_list), key=lambda pair: pair[0], reverse=True)
                    #filters_list = [fil[1] for fil in temp_filters]
                    #temp_docs = sorted(zip(match, docs), key=lambda pair: pair[0], reverse=True)
                    #docs = [doc[1] for doc in temp_docs]
                    #match = [doc[0] for doc in temp_docs]

                specified.append(keyword)
                original_filters[keyword] = [new_key]
            else:
                contained_pressure = True
                specified.append(keyword)
                original_filters[keyword] = []
            keyword = self.filters_difference(filters_list[:10], specified)

        # Treat the special set of pressure score questions
        if "pressure" in original_filters and original_filters["pressure"] == []:
            contained_pressure = True
        print(contained_pressure)
        pressure_result = ""
        if contained_pressure and "Crop" in original_filters:
            pr = self.pressure_score_generator.calculate_pressure_score(
                original_filters["Crop"][0], self.history)
            print(pr)
            pressure_level = pr[0]
            text = pr[1]
            match = [match[i] + 2 if (("pressure" in filters_list[i].keys()) and (
                pressure_level in filters_list[i]["pressure"])) else match[i] for i in range(len(filters_list))]
            match = [match[i] + 2 if (("pressure" in filters_list[i].keys()) and (
                filters_list[i]["pressure"] == [pressure_level])) else match[i] for i in range(len(filters_list))]
            pressure_result = pressure_result + text
        sorted_docs = sorted(
            zip(match, docs), key=lambda pair: pair[0], reverse=True)
        for doc in sorted_docs:
            print(doc[1].text)
            print(doc[1].meta)
        result_docs = [doc[1] for doc in sorted_docs]
        if len(result_docs) >= 1:
            result_docs[0].text = pressure_result + "\n" + result_docs[0].text
        return result_docs[:3]

    def run(self, **kwargs):
        with self.update_lock:
            #print("Running Question Generator")
            original_filters = self.individualFiltersGenerator(kwargs["query"])
            print(kwargs["query"])
            print(original_filters)
            specified = list(original_filters.keys())
            return ({"result": self.furtherQuestions(kwargs["documents"], specified, original_filters)}, "output_1")

    def update_components(self):
        with self.update_lock:
            self.setup_keyword_extractor()
            self.pressure_score_generator.update_pressure_table()
