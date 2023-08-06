import re


class PuncRemover:
    """
    remove punctuation from texts.
    """

    def __init__(self):
        # TODO:should save these rules in an external file in /config directory
        # define patterns for detecting punctuations
        self.punctuation_list = []
        self.punctuations = r')(}{:؟!،؛»«.' + r"/<>?.,:;"
        self.punctuations = '[' + self.punctuations + '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' + ']'
        self.pattern = '\s*' + self.punctuations + '+' + '\s*'

    def normalize(self, doc_string):
        """

        Parameters
        ----------
        doc_string: str
                input string

        Returns
        -------
        str:
            normalized_string :  string without punctuations.
        """

        # read text and convert to string without punctuations.
        normalized_string = self.convert_punctuation(text_line=doc_string)

        return normalized_string

    def convert_punctuation(self, text_line):
        # find punctuations and replace them with space
        text_line = re.sub(self.pattern, " ", text_line)

        return text_line
