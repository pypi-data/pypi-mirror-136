import re


class Abbreviation:
    """
    convert persioan abbreviation to words.
    """

    def __init__(self):
        # TODO : should save this hardcode strings in a .JSON file in /config.
        self.abbreviation_rules = r'( ه ق )|( ه ش )|( ه.ق )|( ه.ش )|( ع )|( ره )|(\(ه ش\))|(\(ه ق\))|(\(ه.ش\))|(\(ه.ق\))|(\(ره\))|(\(ع\))|( ه ق )|( ه ش )|( ه.ق. )|( ه.ش. )|( ره )|(\(ه ش\))|(\(ه ق\))|(\(.ه.ش\))|(\(ه.ق.\))|(\(ره\))|(\(ع\))'
        self.abbreviation_dictionary = {
            'هق': ' هجری قمری ',
            'هش': ' هجری شمسی ',
            'ره': ' رحمه الله ',
            'ع': ' علیه السلام '
        }

    def normalize(self, doc_string):
        """
        Parameters
        ----------
        doc_string : input string

        Returns
        -------
        string
            normalized_string
        """
        normalized_string = self.find_abbreviation_part(text_line=doc_string)

        return normalized_string

    def find_abbreviation_part(self, text_line) -> str:
        """
        find abbreviation part in string with some rules.

        Parameters
        ----------
        text_line: str

        Returns
        -------
        string
            content_new
        """

        content_new = re.sub(self.abbreviation_rules, lambda x: self.abbreviation_converter(x.group()),
                             " " + text_line + " ")

        return content_new.lstrip().strip()

    def abbreviation_converter(self, input_data) -> str:
        """
        replace abbreviation with words in dictionary.

        Parameters
        ----------
        input_data : str

        Returns
        -------
        string

        """
        try:
            return self.abbreviation_dictionary[re.sub('\W+', "", input_data)]
        except:
            return input_data
