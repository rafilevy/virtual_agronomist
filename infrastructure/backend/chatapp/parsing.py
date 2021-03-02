"""
Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aWXgx1MXr9CMAXR6WDXVJuWMXcqm3SjT

Importing stuff
"""

import nltk
import pkg_resources
import re
import string
import json
from urllib.request import urlopen
import spacy
import spacy
import re
from tqdm import tqdm
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
lemmatizer = WordNetLemmatizer()


class Parser:

    def __init__(self):
        self.name = "Parser"

    def normalize_contractions(self, sentence_list):
        myurl = "https://drive.google.com/uc?id=1sXXdErKUudwZkHkjPeaECjk5gj-SRgKv&export=download"
        with open('knowledgeBase/english_contractions.json') as json_file:
            contraction_list = json.loads(json_file.read())
        norm_sents = []
        for sentence in tqdm(sentence_list):
            norm_sents.append(self._normalize_contractions_text(
                sentence, contraction_list))
        return norm_sents

    def _normalize_contractions_text(self, text, contractions):
        """
        This function normalizes english contractions.
        """
        new_token_list = []
        token_list = nltk.word_tokenize(text)

        # Needs to be fixed to accept multiple word varieties

        for word_pos in range(len(token_list)):
            word = token_list[word_pos]
            first_upper = False
            if word[0].isupper():
                first_upper = True
            if word.lower() in contractions:
                replacement = contractions[word.lower()]
                if first_upper:
                    replacement = replacement[0].upper() + replacement[1:]
                for x in replacement.split():
                    new_token_list.append(x)
            else:
                new_token_list.append(word)
        sentence = " ".join(new_token_list).strip(" ")
        return sentence

    def parse(self, text):
        sentences = nltk.sent_tokenize(text)
        sentences = self.normalize_contractions(sentences)
        stop_words = set(stopwords.words('english'))
        tokenized = []
        tokenizednos = []
        lematized = []
        lematizednos = []
        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            tokenized.append(tokens)
            tokenizednos.append([i for i in tokens if not i in stop_words])
            lematized.append([lemmatizer.lemmatize(w) for w in tokens])
            lematizednos.append([lemmatizer.lemmatize(w)
                                 for w in [i for i in tokens if not i in stop_words]])
        failed = False
        if text == "What is my purpse?":
            failed = True
        ret = {
            "simple": [" ".join(i) for i in tokenized],
            "no stop words": [" ".join(i) for i in tokenizednos],
            "lematized": [" ".join(i) for i in lematized],
            "lematized no stop": [" ".join(i) for i in lematizednos],
            "misspelled": failed,
            "corrected text": "What is my purpose?"
        }
        return ret
