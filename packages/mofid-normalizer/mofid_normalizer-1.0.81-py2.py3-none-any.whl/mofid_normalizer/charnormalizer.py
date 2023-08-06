import string
import re
import json
import os


class CharNormalizer:
    """
    customizable character normalizer class
    """

    def __init__(self, config_file):
        """

        Parameters
        ----------
        config_file : path to the JSON file, that contains characters mappings.
        """

        # TODO: should save these rules as external files at /config file
        # Define and create patterns to detect punctuations for normalization
        self.punctuations = r')(}{:؟!،؛»«.' + r"/<>?.,:;"
        self.punctuations = '[' + self.punctuations + string.punctuation + ']'
        self.punctuations = self.punctuations.replace("@", "")
        self.pattern = '\s*' + self.punctuations + '+' + '\s*'

        # list of characters and their mappings.
        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"

        # read files and create list of mappings.
        with open(config_file) as f:
            mapper_tmp = json.load(f)
        self.char_mapper = {}
        for i in mapper_tmp['Mapper']:
            self.char_mapper.update(mapper_tmp['Mapper'][i])

        # create rules for character mappings.
        self.rule = "|".join(self.char_mapper.keys())
        self.rule = r"(" + self.rule + r")"

    def sub_alphabets(self, doc_string) -> str:
        """
        mapping characters
        Parameters
        ----------
        doc_string : str

        Returns
        -------
        str:
        text with normal characters.
        """
        normalized_text = re.sub(self.rule, lambda m: self.char_mapper.get(str(m.group()), str(m.group())),
                                 str(doc_string))
        return normalized_text

    def normalize(self, doc_string) -> str:
        """

        Parameters
        ----------
        doc_string : str
            input text

        Returns
        -------
        str:
            normalized_string
        """

        # remove extra spaces and adding spaces before and after some special punctuations.
        doc_string = re.sub(self.pattern, self.add_space, doc_string)

        # mapping characters
        normalized_string = self.sub_alphabets(doc_string)

        return normalized_string

    def add_space(self, mystring) -> str:
        """
        adding some necessary spaces.

        Parameters
        ----------
        mystring : str

        Returns
        -------
        str:
            mystring
        """
        mystring = mystring.group()  # this method return the string matched by re
        mystring = mystring.strip(' ')  # ommiting the whitespace around the pucntuation
        mystring = " " + mystring + " "  # adding a space after and before punctuation
        return mystring
