from num2fawords import words
import re
from datetime import datetime
import random


class Time2String:
    """
    convert time (like: 10:30) to string format (like: ده و سی دقیقه)
    """

    def __init__(self):
        # TODO:should save these rules in an external file in /config directory
        self.time_rules = r'( ([0-1]?[0-9]|2[0-3])( +)?:( +)?[0-5]?[0-9](( +)?:( +)?[0-5]?[0-9])?) | (([0-5]?[0-9])' \
                          r'( +)?:( +)?([0-5]?[0-9]) )'
        self.time_format = ['%H:%M:%S', '%H:%M', '%M:%S']
        self.minute_dictionary = {15: "ربع", 30: "نیم"}

    def normalize(self, doc_string) -> str:
        """

        Parameters
        ----------
        doc_string : str

        Returns
        -------
        str:
            normalized_string
        """
        # find times in string and convert them to string.
        normalized_string = self.find_time_part(text_line=doc_string)
        # remove extra spaces.
        normalized_string = re.sub(r" +", " ", normalized_string)

        return normalized_string

    def find_time_part(self, text_line="") -> str:

        # find times in string with rules and convert them.
        converted_time = re.sub(self.time_rules, lambda x: self.time_digit2string(x.group()), " " + text_line + " ")

        return converted_time

    def minute_converter(self, time):
        # randomly convert 30,15 to نیم /ربع

        rnd = random.choices([1, 2], weights=(0.6, 0.4), k=1)
        if rnd[0] == 2 and time.second == 0:
            return self.minute_dictionary[time.minute]

        return words(time.minute) + " دقیقه"

    def time_digit2string(self, input_time) -> str:
        """

        Parameters
        ----------
        input_time : str, in time format, E.X.: 10:23

        Returns
        -------
        str
        """

        # remove spaces from input time
        input_time = re.sub(" ", "", input_time)

        for form in self.time_format:

            # try convert times to string
            try:
                # convert input time to standard format
                d = datetime.strptime(input_time, form)

                # convert hour,minute,second
                hour = words(d.hour) + " و " if words(d.hour) != "صفر" else ""
                minute = words(d.minute) + " دقیقه" if d.minute not in [15, 30] else self.minute_converter(d)
                second = "و " + words(d.second) + " ثانیه " if str(words(d.second)) != 'صفر' else ''

                return " " + hour + " " + minute + " " + second

            except ValueError:
                # if the format of input_time don't match with standard format
                continue

        return " " + input_time + " "
