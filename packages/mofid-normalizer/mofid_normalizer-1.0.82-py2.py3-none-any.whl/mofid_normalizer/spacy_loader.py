from spacy import Language

from .add_vocab_word import VocabConfig
from .charnormalizer import CharNormalizer
from .date2string import Date2String
from .time2string import Time2String
from .num2string import Num2String
from .abbreviation import Abbreviation
from .punctuation_remover import PuncRemover
from .affix_norm import AffixNorm
# from .spell_checker import SpellCheck
from .tokenizer import Tokenizer as ParsivarTokenizer
from .mapping_words import WordMapper
import spacy
import os


# @Language.factory("disabletokenizer")
class WhitespaceTokenizer:
    """
    Spacy tokenized input string in default mode, for some
    processes like spell-checker and affix-normalizer,
    we need whole string, so we should prevent this action with this class.
    """

    def __init__(self, vocab):
        self.vacab = vocab

    def __call__(self, string):
        return string


# @spacy.registry.tokenizers("whitespace_tokenizer")
# def create_whitespace_tokenizer():
#     def create_tokenizer(nlp):
#         return WhitespaceTokenizer(nlp)
#
#     return create_tokenizer

# @Language.factory("CustomSentenceTokenizer")
# class CustomSentenceTokenizer():
# """we can add a custom sentence tokenizer to the Spacy with this class as a default string tokenizer"""
#     def __init__(self):
#         self.tokenizer = parsivar_tokenizer()
#
#     def __call__(self, string):
#         return self.tokenizer.tokenize_sentences(string)
# nlp.tokenizer = disabletokenizer()
# nlp.tokenizer_sentence = CustomSentenceTokenizer()


# Character-normalizer block :

class NormalizerClass:
    """
    Character-normalizer input string class
    Attributes
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    config_file : path to the JSON file, that contains character mappings.
    """

    def __init__(self, nlp: Language, config_file: str):
        """

        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        config_file : path to the JSON file, that contains character mappings.
        """
        self.config_file = config_file
        self.normalizer = CharNormalizer(config_file)

    def __call__(self, doc) -> str:
        """

        Parameters
        ----------
        doc : input string

        Returns
        -------
        character normalized string

        """
        return self.normalizer.normalize(doc)


@Language.factory("char_normalizer", default_config={"config_file": str})
def char_normalizer(nlp: Language, name: str, config_file: str):
    """
    To add a new class rule to the Spacy project, use this format and add it with this function.

    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    config_file : path to the JSON file, that contains character mappings.

    Returns
    -------
    NormalizerClass : character normalized string
    """
    return NormalizerClass(nlp, config_file)


# Date2Str block:
class DateString:
    """
    convert date (like 10/2/2010) to strings.
    Attributes
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    """

    def __init__(self, nlp: Language):
        """

        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        """
        self.date_2_string = Date2String()

    def __call__(self, doc) -> str:
        """

        Parameters
        ----------
        doc  : input string

        Returns
        -------
        The input string with the Date part converted to words.
        """
        return self.date_2_string.normalize(doc)


@Language.factory("date2str", default_config={})
def date2str(nlp: Language, name: str):
    """
    To add a new class rule to the Spacy project, use this format and add it with this function.
    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    name : some name

    Returns
    -------
    The input string with the Date part converted to words.

    """
    return DateString(nlp)


# Num2Str block:
class NumString:
    """
       convert date (like -2568) to strings.
       Attributes
       ----------
       nlp : this is a Spacy package for languages, here we use Persian.
       """

    def __init__(self, nlp: Language):
        """

        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        """
        self.num_2_string = Num2String()

    def __call__(self, doc) -> str:
        """

        Parameters
        ----------
        doc  : input string

        Returns
        -------
        The input string with the Number part converted to words.
        """
        return self.num_2_string.normalize(doc)


@Language.factory("num2str", default_config={})
def num2str(nlp: Language, name: str):
    """
    To add a new class rule to the Spacy project, use this format and add it with this function.
    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    name : some name

    Returns
    -------
    The input string with the Number part converted to words.

    """
    return NumString(nlp)


# Time2Str block
class TimeString:
    """
       convert time (like 20:30) to strings.
       Attributes
       ----------
       nlp : this is a Spacy package for languages, here we use Persian.
       """

    def __init__(self, nlp: Language):
        """

        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        """
        self.time_2_string = Time2String()

    def __call__(self, doc) -> str:
        """

        Parameters
        ----------
        doc  : input string

        Returns
        -------
        Input string with converted Time part to string part.
        """
        return self.time_2_string.normalize(doc)


@Language.factory("time2str", default_config={})
def time2str(nlp: Language, name: str):
    """
    To add a new class rule to the Spacy project, use this format and add it with this function.
    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    name : some name

    Returns
    -------
    The input string with the Time part converted to words.

    """
    return TimeString(nlp)


# Abbreviation2Word block:
class Abbreviation2Word:
    """
    convert Abbreviation words (like ه.ق) to strings.
    Attributes
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    """

    def __init__(self, nlp: Language):
        """

        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        """
        self.Abbreviation_2_word = Abbreviation()

    def __call__(self, doc) -> str:
        """

        Parameters
        ----------
        doc  : input string

        Returns
        -------
        The input string with the abbreviation part converted to words.
        """
        return self.Abbreviation_2_word.normalize(doc)


@Language.factory("abbreviation2word", default_config={})
def Abbreviation2word(nlp: Language, name: str):
    """
    To add a new class rule to the Spacy project, use this format and add it with this function.
    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    name : some name

    Returns
    -------
    The input string with the Abbreviation part converted to words.

    """
    return Abbreviation2Word(nlp)


# Tokenizer block:
ParsivarTokenizer = ParsivarTokenizer()


@Language.component("word_level_tokenizer")
def word_level_tokenizer(doc) -> str:
    """
    Tokenizing strings with a custom Parsivar tokenizer.
    Parameters
    ----------
    doc : input String

    Returns
    -------
    list of tokens
    """
    return ParsivarTokenizer.tokenize_words(doc)


# Punctuation-Remover block:
class PunctuationRemover:
    """
    Remove Punctuations (like .,) from strings.
    Attributes
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    """

    def __init__(self, nlp: Language):
        """
        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        """
        self.punc_remover = PuncRemover()

    def __call__(self, doc):
        """
        Parameters
        ----------
        doc  : input string

        Returns
        -------
        The input string without punctuations.
        """
        return self.punc_remover.normalize(doc)


@Language.factory("punctuation_remover", default_config={})
def punctuation_remover(nlp: Language, name: str):
    """
    To add a new class rule to the Spacy project, use this format and add it with this function.
    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    name : some name

    Returns
    -------
    The input string without punctuations.

    """
    return PunctuationRemover(nlp)


# -----------------------------------------------------------

class Affix2Norm:
    """
    Separate suffixes and prefixes from words.
    Attributes
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    config_file : path to the JSON file, that contains character mappings.
    double_postfix_joint : some words like کتابهایتان have 2 postfixes we can decide how to struggle with these words.
    """

    def __init__(self, nlp: Language, config_file: str, double_postfix_joint: bool, separator_character: str):
        """

        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        config_file : path to the JSON file, that contains affix list.
        double_postfix_joint : some words like کتابهایتان have 2 postfixes we
        can decide how to struggle with these words.
        """

        self.config_file = config_file
        self.double_post_joint = double_postfix_joint
        self.separator_character = separator_character
        self.affix = AffixNorm(self.config_file, self.double_post_joint, self.separator_character)

    def __call__(self, doc) -> str:
        """

        Parameters
        ----------
        doc : input string

        Returns
        -------
        divided Combined words with space or half-space
        """

        return self.affix.normalize(doc)


@Language.factory("affix2norm",
                  default_config={"config_file": str, "double_postfix_joint": bool, "separator_character": str})
def affix2norm(nlp: Language, name: str, config_file: str, double_postfix_joint: bool, separator_character: str):
    """

    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    config_file : path to the JSON file, that contains Affixes list that should be changed.
    double_postfix_joint : some words like کتابهایتان have 2 postfixes we can decide how to struggle with these words.

    Returns
    -------
    divided Combined words with space or half-space
    """

    return Affix2Norm(nlp, config_file, double_postfix_joint, separator_character)


# -----------------------------------------------------------

class VocabConfigure:

    def __init__(self, nlp: Language, add_list: list, remove_list: list):
        self.add_list = add_list
        self.remove_list = remove_list

        self.config = VocabConfig(self.add_list, self.remove_list)

    def __call__(self,doc):
        self.config.modifier()
        return doc

@Language.factory("vocab_config",
                  default_config={"add_list": list, "remove_list": list})
def vocab_config(nlp: Language,name: str, add_list: list, remove_list: list):
    return VocabConfigure(nlp, add_list, remove_list)


# -----------------------------------------------------------

class MappingWord:
    """
    mapping some words to desired words
    Attributes
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    config_file : path to the JSON file, that contains Words mappings.
    half_space_char : some character like space,half-space,none or other characters
    """

    def __init__(self, nlp: Language, config_file: str, half_space_char: str):
        """

        Parameters
        ----------
        nlp : this is a Spacy package for languages, here we use Persian.
        config_file : path to the JSON file, that contains Words mappings.
        half_space_char : some character like space,half-space,none or other characters
        """
        self.config_file = config_file
        self.half_space_char = half_space_char
        self.mapper = WordMapper(self.config_file, half_space_char)

    def __call__(self, doc):
        """

        Parameters
        ----------
        doc : Input String

        Returns
        -------
        String
        """
        return self.mapper.normalize(doc)


@Language.factory("word_mapper", default_config={"config_file": str, "half_space_char": str})
def word_mapper(nlp: Language, name: str, config_file: str, half_space_char):
    """

    Parameters
    ----------
    nlp : this is a Spacy package for languages, here we use Persian.
    config_file : path to the JSON file, that contains Words mappings.
    half_space_char : some character like space,half-space,none or other characters
    Returns
    -------
    Strings
    """
    return MappingWord(nlp, config_file, half_space_char)


# Spell-Checker block:
# class SpellCheker:
#     def __init__(self, nlp: Language):
#         self.spell = SpellCheck()
#
#     def __call__(self, doc):
#         return self.spell.spell_corrector(doc)
#
# @Language.factory("spell_checker", default_config={})
# def spell_checker(nlp: Language, name: str):
#     return SpellCheker(nlp)


# Create spacy instance for persian language
nlp = spacy.blank("fa")
# default config file path
conf_path = os.path.dirname(os.path.realpath(__file__)) + "/config/"

# should remove default spacy tokenizer from start of pipeline.
nlp.tokenizer = WhitespaceTokenizer(nlp)
# Start adding Modules to pipeline,Notice that ORDER is important.
nlp.add_pipe("char_normalizer", first=True,
             config={"config_file": conf_path + 'character_mappings.json'})
# TODO: if enable Spell-Checker Module should change below code
# nlp.add_pipe("spell_checker", after="char_normalizer", config={})
# nlp.add_pipe("vocab_config", after="spell_checker", config={})
nlp.add_pipe("vocab_config", after="char_normalizer", config={"add_list": [], "remove_list": []})
nlp.add_pipe("date2str", after="vocab_config", config={})
nlp.add_pipe("time2str", after="date2str", config={})
nlp.add_pipe("num2str", after="time2str", config={})
nlp.add_pipe("abbreviation2word", after="num2str", config={})
nlp.add_pipe("affix2norm", after="abbreviation2word",
             config={"config_file": conf_path + 'affix.json', "double_postfix_joint": True,
                     "separator_character": '#'})
nlp.add_pipe("word_mapper", after="affix2norm",
             config={"config_file": conf_path + 'word_mappings.json', "half_space_char": "  "})

nlp.add_pipe("punctuation_remover", after="abbreviation2word", config={})
nlp.add_pipe("word_level_tokenizer")

# also can create an empty instance of spacy pipeline and customize it on your own Modules
nlp_blank = spacy.blank("fa")
nlp_blank.tokenizer = WhitespaceTokenizer(nlp_blank)
