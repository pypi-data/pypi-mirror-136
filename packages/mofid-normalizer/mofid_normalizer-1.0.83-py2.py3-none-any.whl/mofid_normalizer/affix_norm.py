from re import sub
import os
from .data_helper import DataHelper
import re
from .stemmer import FindStems
import json


class AffixNorm:
    """Nouns and verbs are divided into stems, prefixes, and postfixes"""

    def __init__(self, config_file=os.path.dirname(os.path.realpath(__file__)) + "/config/affix.json",
                 double_postfix_joint=False,
                 separator_character="\u200c",
                 # statistical_space_correction=False,
                 ):
        """

        Parameters
        ----------
        config_file : list
                The list of affixes that should be normalized in words based on rules.
        double_postfix_joint: boolean
                some words like کتابهایتان have 2 postfixes we can decide how to struggle with these words.
        """
        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        # self.statistical_space_correction = statistical_space_correction
        self.separator_character = separator_character
        with open(config_file) as f:
            self.affix_list = json.load(f)

        self.stemmer = FindStems(config_file=config_file, double_postfix_joint=double_postfix_joint,
                                 separator_character=self.separator_character)

        # TODO: we can add statistical space correction in future.
        # train_file_path = "resource/tokenizer/Bijan_khan_chunk.txt",
        # token_merger_path = "resource/tokenizer/TokenMerger.pckl",
        # if self.statistical_space_correction:
        #     self.data_helper = DataHelper()
        #     self.token_merger_path = self.dir_path + token_merger_path
        #     self.train_file_path = train_file_path
        #
        #     if os.path.isfile(self.token_merger_path):
        #         self.token_merger_model = self.data_helper.load_var(self.token_merger_path)
        #     elif os.path.isfile(self.train_file_path):
        #         self.token_merger_model = self.token_merger.train_merger(self.train_file_path, test_split=0)
        #         self.data_helper.save_var(self.token_merger_path, self.token_merger_model)

    def space_correction(self, doc_string):
        """
        some words in sentences should be together, like کتاب and ها,
        in this function words will add to each other based on rules.

        Parameters
        ----------
        doc_string: str

        Returns
        -------
        str

        """

        a00 = r'^(' + "|".join(self.affix_list["space_jointer_to_next"]) + r')( )'
        b00 = r'\1‌'
        c00 = sub(a00, b00, doc_string)
        a0 = r'( )(' + "|".join(self.affix_list["space_jointer_to_next"]) + r')( )'
        b0 = r'\1\2‌'
        c0 = sub(a0, b0, c00)
        a1 = r'( )(' + "|".join(self.affix_list["space_jointer_to_previous"]) + r')( )'
        b1 = r'‌\2\3'
        c1 = sub(a1, b1, c0)
        a2 = r'( )' + "|".join(self.affix_list["space_jointer_to_next_previous"]) + r'( )'
        b2 = r'‌\2‌'
        c2 = sub(a2, b2, c1)
        a3 = r'( )(' + "|".join(self.affix_list["space_jointer_to_previous_plus"]) + r')( )'
        b3 = r'‌\2\3'
        c3 = sub(a3, b3, c2)

        return c3

    def normalize(self, doc_string):
        """
        splits postfix and prefix of word.

        Parameters
        ----------
        doc_string : str, input string

        Returns
        -------
        str, normalized string.
        """

        # Corrects the spacing between words in a string, based on some rules.
        doc_string = self.space_correction(doc_string)
        # find Prefix and Postfix of a word.
        normalized_string = self.word_level_normalizer(text_line=doc_string)
        normalized_string = self.sentence_level_normalizer(text_line=normalized_string)

        return normalized_string

    def sentence_level_normalizer(self, text_line):
        """

        Parameters
        ----------
        text_line: str , input string.

        Returns
        -------
        str: normalized version of sentences.
        """
        # find and remove ی in the context
        text_line = re.sub(r"ه( +|\u200c)ی( +|\u200c)", "ه ", text_line)
        return text_line

    def word_level_normalizer(self, text_line):
        """
        find Prefix and Postfix of a word.

        Parameters
        ----------
        text_line : str, input string.

        Returns
        -------
        str:  normalized version of words (Sticky version of the words)
        """
        # split input string
        text_line_list = text_line.split()

        text = ' '
        for word in text_line_list:
            # stemming each word
            tmp = re.sub("\u200c", "", word)
            result = self.stemmer.convert_to_stem(tmp)
            # concat words
            text += result + ' '

        # remove extra spaces.
        text = re.sub(r' +', ' ', text)
        return "".join(text.rstrip().lstrip())
