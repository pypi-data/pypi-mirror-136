import os
import json
import re


class WordMapper:
    """
    mapping words to desired words.
    """

    def __init__(self, config_file=os.path.dirname(os.path.realpath(__file__)) + "/config/word_mappings.json",
                 half_space_char='\u200c'
                 ):
        """
        Parameters
        ----------
        config_file : json
            word mappings list
        half_space_char : str
            some special characters
        """
        with open(config_file) as f:
            self.dictionary_mapping = json.load(f)

        # define patterns
        self.half_space_char = half_space_char
        self.rule = "|".join(self.dictionary_mapping.keys())
        self.rule = r"(?<!\w)(" + self.rule + r")(?!\w)"

    def normalize(self, doc_string):
        """
        Parameters
        ----------
        doc_string : str
            input string
        """
        # find desired words and replace them with new words.
        text = re.sub(self.rule, lambda m: self.dictionary_mapping.get(str(m.group()), str(m.group())), str(doc_string))

        # replace dis-jointer(default: \u200c) with new character.
        text = re.sub(r"\u200c", self.half_space_char, text)
        # remove extra spaces
        text = re.sub(r' +', ' ', text)

        # remove spaces from start and end of string.
        return "".join(text.rstrip().lstrip())
