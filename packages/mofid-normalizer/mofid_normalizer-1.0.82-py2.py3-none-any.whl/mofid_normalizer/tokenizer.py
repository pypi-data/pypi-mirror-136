import re


class Tokenizer:

    """tokenize strings in word level and sentence level"""

    def __init__(self):
        pass

    def tokenize_words(self, doc_string):
        """
        tokenize string based on space and half-space

        Parameters
        ----------
        doc_string : str
            input string

        Returns
        -------
        list:
        token_list : list of tokens in string
        """
        token_list = doc_string.strip().split()
        token_list = [x.strip("\u200c") for x in token_list if len(x.strip("\u200c")) != 0]
        return token_list

    def tokenize_sentences(self, doc_string):
        """
        tokenize string based on sentences with some rules.

        Parameters
        ----------
        doc_string : str
                input string

        Returns
        -------
        list:
            doc_string : list of sentences.
        """
        # finding the numbers and replace with special character
        pattern = r"[-+]?\d*\.\d+|\d+"
        nums_list = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, 'floatingpointnumber', doc_string)

        # finding the punctuations and add space before and after punctuations
        pattern = r'([!\.\?؟]+)[\n]*'
        tmp = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, self.add_tab, doc_string)

        # finding colon and new line then add space before and after that
        pattern = r':\n'
        tmp = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, self.add_tab, doc_string)

        # finding semi-colon and new line then add space before and after that
        pattern = r';\n'
        tmp = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, self.add_tab, doc_string)

        # finding persian semi-colon and new line then add space before and after that
        pattern = r'؛\n'
        tmp = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, self.add_tab, doc_string)

        # finding persian new lines then add space before and after that
        pattern = r'[\n]+'
        doc_string = re.sub(pattern, self.add_tab, doc_string)

        for number in nums_list:
            pattern = 'floatingpointnumber'
            doc_string = re.sub(pattern, number, doc_string, 1)

        # split input string based on tab.
        doc_string = doc_string.split('\t\t')
        doc_string = [x for x in doc_string if len(x) > 0]
        return doc_string

    def add_tab(self, mystring):
        mystring = mystring.group()  # this method return the string matched by re
        mystring = mystring.strip(' ')  # omitting the whitespace around the punctuation
        mystring = mystring.strip('\n')  # omitting the newline around the punctuation
        mystring = " " + mystring + "\t\t"  # adding a space after and before punctuation
        return mystring
