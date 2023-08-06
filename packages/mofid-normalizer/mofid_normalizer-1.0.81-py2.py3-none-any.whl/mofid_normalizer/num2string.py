from num2fawords import words
import re


class Num2String:
    """convert number to string in different formats."""
    def __init__(self):
        # TODO:should save these rules in an external file in /config directory
        self.number_rules = r'( +| -| )(((\d{1,30})?[./]\d{1,30} )|(\d{1,30} ))'

    def normalize(self, doc_string):
        normalized_string = self.find_number_part(text_line=doc_string)

        return normalized_string

    def find_number_part(self, text_line):
        """
        find numbers in a string.

        Parameters
        ----------
        text_line: str
            input text

        Returns
        -------
        str
        """
        text_line = " " + text_line + " "
        # find and replace numbers with strings
        content_new = re.sub(self.number_rules, lambda x: self.number_converter(x.group()), text_line)
        # remove extra spaces
        content_new = re.sub(' +', ' ', content_new)

        # remove space from start and end of string.
        return content_new.lstrip().strip()

    def number_converter(self, input_data):
        """
        convert numbers in a different format to string.

        Parameters
        ----------
        input_data: float
                input number

        Returns
        -------
        str:
            number in string.
        """
        try:
            return " " + words(input_data, positive='', negative='منهای ', fraction_separator=' ممیز ',
                               ordinal_denominator=False, decimal_separator=' ممیز ') + " "

        except ValueError:
            return input_data
