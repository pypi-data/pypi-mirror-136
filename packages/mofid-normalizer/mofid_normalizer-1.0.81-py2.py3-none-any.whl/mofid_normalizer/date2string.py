from num2fawords import words, ordinal_words
import re

import random


class Date2String:
    """convert date in a text to string. E.X : 10/2/1395 -> ده‌ام اردیبهشت سال هزارو سیصد و نود و پنج"""

    def __init__(self):
        # TODO: should save these rules as an external .Json file in /config.
        self.month_names = {'شمسی': {1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4:
            "تیر", 5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"},
                            'قمری': {1: "محرم", 2: "صفر", 3: "ربیع‌الاول", 4:
                                "ربیع‌الثانی", 5: "جمادی‌الاول", 6: "جمادی‌الثانی", 7:
                                         "رجب", 8: "شعبان", 9: "رمضان", 10:
                                         "شوال", 11: "ذیقعده", 12: "ذیحجه"},

                            'میلادی': {1: "ژانویه", 2: "فوریه", 3: "مارچ", 4:
                                "آپریل", 5: "می", 6: "جون", 7:
                                           "جولای", 8: "آگوست", 9: "سپتامبر", 10:
                                           "اکتبر", 11: "نوامبر", 12: "دسامبر"}}

        self.num_dict = {"صد": 100, "هزار": 1000, "میلیون": 1000000, "دویست": 200,
                         "ده": 10, "نه": 9, "هشت": 8, "هفت": 7, "شش": 6, "پنج": 5,
                         "چهار": 4, "سه": 3, "دو": 2, "یک": 1, "یازده": 11, "سیزده": 13,
                         "چهارده": 14, "دوازده": 12, "پانزده": 15, "شانزده": 16, "هفده": 17,
                         "هجده": 18, "نوزده": 19, "بیست": 20, "سی": 30, "چهل": 40, "پنجاه": 50,
                         "شصت": 60, "هفتاد": 70, "نود": 90, "سیصد": 300, "چهارصد": 400,
                         "پانصد": 500, "ششصد": 600, "هفتصد": 700, "هشتصد": 800, "نهصد": 900,
                         "هشتاد": 80, " ": 0, "میلیارد": 1000000000,
                         "صدم": 100, "هزارم": 1000, "دویستم": 200,
                         "دهم": 10, "نهم": 9, "هشتم": 8, "هفتم": 7, "ششم": 6, "پنجم": 5,
                         "چهارم": 4, "سوم": 3, "دوم": 2, "یکم": 1, "اول": 1, "یازدهم": 11, "سیزدهم": 13,
                         "چهاردهم": 14, "دوازدهم": 12, "پانزدهم": 15, "شانزدهم": 16, "هفدهم": 17,
                         "هجدهم": 18, "نوزدهم": 19, "بیستم": 20, "چهلم": 40, "پنجاهم": 50,
                         "شصتم": 60, "هفتادم": 70, "نودم": 90, "سیصدم": 300, "چهارصدم": 400,
                         "پانصدم": 500, "ششصدم": 600, "هفتصدم": 700, "هشتصدم": 800, "نهصدم": 900,
                         "هشتادم": 80}

        self.format_list = ['%Y-%m-%d', '%Y-%d-%m', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y/%d/%m', '%d/%m/%Y',
                            '%m/%d/%Y']

        self.date_rules = r'(((0[1-9]|1[012]|\b[1-9])( )*[-/.]( )*(0[1-9]|[12][0-9]|3[01]|[1-9])( )*[-/.]( )*[11-20]\d\d\d)|((0[0-9]|[12][0-9]|3[01]|\b[1-9])( )*[-/.]( )*(0[1-9]|1[012]|[1-9])( )*[-/.]( )*([11-20]\d\d\d))|(([11-20]\d\d\d)( )*[-/.]( )*(0[1-9]|1[012]|[1-9])( )*[-/.]( )*(0[1-9]|[12][0-9]|3[01]|[1-9]\b))|(([11-20]\d\d\d)( )*[-/.]( )*(0[1-9]|[12][0-9]|3[01]|[1-9])( )*[-/.]( )*(0[1-9]|1[012]|[1-9]\b)))'

    def normalize(self, doc_string):
        """

        Parameters
        ----------
        doc_string : str
            input text

        Returns
        -------
        str:
            normalized_string: text with converted date to strings.
        """
        normalized_string = self.find_date_part(text_line=doc_string)

        return normalized_string

    def find_date_part(self, text_line=""):
        """
        find time part in strings and convert it to string.

        Parameters
        ----------
        text_line: str

        Returns
        -------
        str:
            converted_text
        """
        converted_text = re.sub(self.date_rules, lambda x: self.date_digit2string(x.group()), text_line)

        return converted_text

    def convert_month(self, month, date_type):
        """
        convert month to string with probability.

        Parameters
        ----------
        month : int
        date_type : str
            type of date (shamsi,ghamari,miladi).
        Returns
        -------
        str:
            month: name of month with some probability
        """
        rnd = random.choices([1, 2, 3], weights=(0.6, 0.3, 0.1), k=1)

        if rnd[0] == 1: return self.month_names[date_type][month]
        if rnd[0] == 2: return self.month_names[date_type][month] + " ماه "
        if rnd[0] == 3: return str(words(month))

    def convert_year(self, year, date_type):
        """
        convert year to string with probability.

        Parameters
        ----------
        year : int
        date_type : str
            date type (shamsi,ghamari,miladi)

        Returns
        -------
        str:
            month: string of year with some probability
        """
        rnd = random.choices([1, 2, 3, 4], weights=(0.4, 0.2, 0.1, 0.2), k=1)
        # just print string of year like: هزار و سیصد و نود و چهار
        if rnd[0] == 1: return words(year)
        # print string of year + سال like : سال هزار و سیصد نود چهار
        if rnd[0] == 2: return "سال " + words(year)
        # print string of year + سال + type of date like :  سال هزار و سیصد و نود چهار هجری شمسی
        if rnd[0] == 3: return "سال " + words(year) + ' ' + date_type
        # print string of year + type of date like :   هزار و سیصد و نود چهار هجری شمسی
        if rnd[0] == 4: return words(year) + ' ' + date_type

    def convert_day(self, day):
        """
        convert day to string with probability.

        Parameters
        ----------
        day: int

        Returns
        -------
        str

        """
        rnd = random.choices([1, 2], weights=(0.4, 0.6), k=1)

        #  پانزده
        if rnd[0] == 1: return words(day)
        # پانزده‌ام
        if rnd[0] == 2: return ordinal_words(day)

    def date_type(self, date):
        """detect format of date"""
        if int(date) < 1410:
            return 'شمسی'
        elif 1550 > int(date) > 1410:
            return 'قمری'
        else:
            return 'میلادی'

    def date_digit2string(self, input_date) -> str:
        """
        find format of date and convert it base on some rules.

        Parameters
        ----------
        input_date : str
            date strings like: 10/2/1350

        Returns
        -------
        str:
            date
        """

        def convert_date(year: int, month: int, day: int):
            # detect type of date (shamsi,ghamari,miladi)

            date_type = self.date_type(int(year))

            month = self.convert_month(int(month), date_type)
            year = self.convert_year(int(year), date_type)
            day = self.convert_day(int(day))

            return day + " " + month + " " + year

        # split string of date to year,month,day
        split_date = re.split("-|/|\.", input_date)

        # Detect format of date, in this condition position 0 of split = year, position 1: month , position 2: day
        if 1000 < int(split_date[0]) < 3000 and 0 < int(split_date[1]) < 13 and 0 < int(split_date[2]) < 32:
            return convert_date(year=int(split_date[0]), month=int(split_date[1]), day=int(split_date[2]))

        # Detect format of date, in this condition position 0 of split = year, position 2: month , position 1: day
        elif 1000 < int(split_date[0]) < 3000 and 0 < int(split_date[2]) < 13 and 0 < int(split_date[1]) < 32:
            return convert_date(year=int(split_date[0]), month=int(split_date[2]), day=int(split_date[1]))
        # Detect format of date, in this condition position 2 of split = year, position 1: month , position 0: day
        elif 1000 < int(split_date[2]) < 3000 and 0 < int(split_date[1]) < 13 and 0 < int(split_date[0]) < 32:
            return convert_date(year=int(split_date[2]), month=int(split_date[1]), day=int(split_date[0]))

        # Detect format of date, in this condition position 2 of split = year, position 0: month , position 1: day
        elif 1000 < int(split_date[2]) < 3000 and 0 < int(split_date[0]) < 13 and 0 < int(split_date[1]) < 32:
            return convert_date(year=int(split_date[2]), month=int(split_date[0]), day=int(split_date[1]))
        else:
            return input_date
