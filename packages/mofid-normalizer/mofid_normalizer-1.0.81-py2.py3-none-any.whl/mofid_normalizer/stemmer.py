import os
import json
import re
from .data_helper import DataHelper


class FindStems:
    """Find Stem ,prefix and postfix of Combined words"""

    def __init__(self, config_file, double_postfix_joint, separator_character):
        """
        Parameters
        ----------
        config_file : config file that contains affix lists.
        double_postfix_joint : some words like کتابهایتان have 2 postfixes we can decide how to struggle with these words.

        """

        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.noun_lex_path = self.dir_path + "resource/stemmer/stem_lex.pckl"
        self.mini_noun_lex_path = self.dir_path + "resource/stemmer/original_parsivar_stem_lex.pckl"
        self.verb_lex_path = self.dir_path + "resource/stemmer/verbStemDict.pckl"
        self.verb_tense_map_path = self.dir_path + "resource/stemmer/stem_verbMap.pckl"
        self.irregular_nouns_path = self.dir_path + "resource/stemmer/stem_irregularNounDict.pckl"
        self.prefix_list_path = self.dir_path + "resource/stemmer/pishvand.txt"
        self.postfix_list_path = self.dir_path + "resource/stemmer/pasvand.txt"
        self.verb_tense_file_path = self.dir_path + "resource/stemmer/verb_tense.txt"
        with open(self.dir_path + "resource/stemmer/verb_tenses.json") as f:
            self.verb_list_tenses = json.load(f)
        self.mokasar_noun_path = self.dir_path + "resource/stemmer/mokasar.txt"
        self.data_helper = DataHelper()
        if (os.path.isfile(self.noun_lex_path) and os.path.isfile(self.verb_lex_path)
                and os.path.isfile(self.verb_tense_map_path) and os.path.isfile(self.irregular_nouns_path)):
            self.noun_lexicon = self.data_helper.load_var(self.noun_lex_path)
            self.mini_lexicon = self.data_helper.load_var(self.mini_noun_lex_path)
            self.verb_lexicon = self.data_helper.load_var(self.verb_lex_path)
            self.verb_tense_map = self.data_helper.load_var(self.verb_tense_map_path)
            self.irregular_nouns = self.data_helper.load_var(self.irregular_nouns_path)

            self.verb_p2f_map, self.verb_f2p_map = self.verb_tense_map[0], self.verb_tense_map[1]

        with open(config_file) as f:
            self.affix_list = json.load(f)
        self.double_postfix_joint = double_postfix_joint
        self.separator_character = separator_character
        self.noun_lexicon.update(self.mini_lexicon)

    def select_candidate(self, candidate_list, lexicon_set=None):
        """
        check if candidate stem is there in vocabulary or not?

        Parameters
        ----------
        candidate_list : list
                list of candidate
        lexicon_set: set
                vocabulary of nouns or verbs

        Returns
        -------
        str:
            selected word
        """
        length = 1000
        selected = ""
        for tmp_candidate in candidate_list:
            if lexicon_set is None and len(tmp_candidate) < length:
                selected = tmp_candidate
                length = len(tmp_candidate)
            elif lexicon_set is not None and (tmp_candidate in lexicon_set):
                if length == 1000:
                    selected = tmp_candidate
                    length = len(tmp_candidate)
                else:
                    if len(tmp_candidate) > length:
                        selected = tmp_candidate
                        length = len(tmp_candidate)
        return selected

    def is_prefix(self, word, prefix):
        """
        check verb has prefix or not, then return true or false.

        Parameters
        ----------
        word: str
            input verb
        prefix: str
            candidate postfix we should check

        Returns
        -------
        Boolean
        """
        word = word.strip("\u200c")
        return word.startswith(prefix)

    def is_postfix(self, word, post):
        """
        check verb has postfix or not, then return true or false

        Parameters
        ----------
        word: str
            input verb
        post: str
            candidate postfix we should check

        Returns
        -------
        Boolean
        """
        word = word.strip("\u200c")
        return word.endswith(post)

    def remove_prefixes(self, word, prefix):
        """
        detect prefix of words based on prefix list pass to the function

        Parameters
        ----------
        word: str
        prefix: list of prefix

        Returns
        -------
        list:
            prefix, list of candidate stem
        """
        word = word.strip("\u200c")
        candidateStem = set({})
        last_el = ''
        for el in prefix:
            if word.startswith(el):
                if len(el) > 0:
                    if len(el) > len(last_el):
                        last_el = el
                        tmp = word[len(el):].strip().strip('\u200c')
                else:
                    tmp = word
                candidateStem.add(tmp)
        return last_el, candidateStem

    def remove_postfixes(self, word, postfix):
        """
        detect postfix of words based on postfix list pass to the function.

        Parameters
        ----------
        word: str
        postfix: list
            list of prefix

        Returns
        -------
        list:
            postfix, list of candidate stem
        """
        word = word.strip("\u200c")
        candidateStem = set({})
        last_el = ''
        for el in postfix:

            if word.endswith(el):
                if len(el) > 0:
                    if len(el) > len(last_el):
                        last_el = el
                        tmp = word[:-len(el)].strip().strip('\u200c')
                        candidateStem = set({})
                        candidateStem.add(tmp)
                else:
                    tmp = word

        return last_el, candidateStem

    def map_irregular_noun(self, word):
        """
        map some irregular word like اعماق : عمق

        Parameters
        ----------
        word: str, input str

        Returns
        -------
        str
        """
        if word in self.irregular_nouns:
            return self.irregular_nouns[word]
        else:

            return word

    def postfix_g(self, word):
        """
        find postfix "گ", like: ستارگان

        Parameters
        ----------
        word: str

        Returns
        -------
        list
        """
        postfix, candidate_list = self.remove_postfixes(word, ["گی", "گان"])

        if len(candidate_list) > 0 and postfix != '' and len(list(candidate_list)[0]) > 1:
            new_word = self.select_candidate(candidate_list)
            new_word = new_word + "ه"

            if new_word in self.noun_lexicon:
                return new_word, postfix

        return [word]

    def verb_part_jointer(self, prefix, postfix, stem):
        """


        Parameters
        ----------
        prefix: list, list of prefix of the verb.
        postfix: list, list of postfix of the verb.
        stem: str,

        Returns
        -------
        output: str, normalized version of verb (Sticky version of the verb)
        """

        output = ''
        for index, i in enumerate(prefix):
            if len(i) < 2 and index == 0 or i in ["خواه", "نخواه"] and i != "":
                output += i
            elif i != "":
                output += i + self.separator_character
        output += stem

        for i in reversed(postfix):
            if i in ["یم", "ید", "ند",
                     "م", "ی", "د", "", "ه"]:
                output += i
            elif i != "":
                output += self.separator_character + i
        return output

    def eltezami_stem_converter(self, new_word):
        """
        For Eltezami, verbs should check some extra rules.

        Parameters
        ----------
        new_word:str , stem of verb

        Returns
        -------
        boolean
            change_status: if the input verb is changed this will change to True.
        str:
            new_word: converted format of verb.
        """
        change_status = False
        if self.is_prefix(new_word, "یا") and new_word not in self.verb_lexicon:
            prefix_word, candidate_list = self.remove_prefixes(new_word, ["یا"])
            new_word = self.select_candidate(candidate_list)
            new_word = "آ" + new_word
            change_status = True
        if self.is_postfix(new_word, "آی") or self.is_postfix(new_word, "ای") and new_word not in self.verb_lexicon:
            postfix_word, candidate_list = self.remove_postfixes(new_word, ["ی"])
            new_word = self.select_candidate(candidate_list)
            change_status = True
        if self.is_prefix(new_word, "ی"):
            prefix_word, candidate_list = self.remove_prefixes(new_word, ["ی"])
            tmp_word = self.select_candidate(candidate_list)
            if tmp_word and ("ا" + tmp_word) in self.verb_lexicon:
                new_word = "ا" + tmp_word
                change_status = True
        return (change_status, new_word)

    def verb_rule_checker(self, input_word):
        """
        check rules for all tenses of verbs.

        Parameters
        ----------
        input_word: str

        Returns
        -------
        str:
            If CAN divide verb based on rules will be return normalized format of that.
        None:
            If CAN'T divide verb based on rules.
        """
        for key, value in self.verb_list_tenses.items():
            prefix_tmp = []
            postfix_tmp = []
            word = input_word
            # See if the word has a specific prefix.
            for key1, value1 in value.items():
                if key1.startswith("postfix"):
                    postfix_word, candidate_list = self.remove_postfixes(word, value1)
                    postfix_tmp.append(postfix_word)

                if key1.startswith("prefix"):
                    prefix_word, candidate_list = self.remove_prefixes(word, value1)
                    prefix_tmp.append(prefix_word)

                if len(candidate_list) > 0:
                    word = self.select_candidate(candidate_list)

            stem = self.select_candidate(candidate_list, self.verb_lexicon)

            if key == "مضارع التزامی و امر":
                result = self.eltezami_stem_converter(word)
                if result[0]:
                    stem = result[1]

            if stem in eval("self." + value["root_vocab"]) and stem is not None:
                if "مضارع التزامی و امر":
                    return self.verb_part_jointer(prefix=prefix_tmp, postfix=postfix_tmp,
                                                  stem=word)

                return self.verb_part_jointer(prefix=prefix_tmp, postfix=postfix_tmp,
                                              stem=stem)
        return None

    def verbs_decomposer(self, word):
        """
        Analyze verbs based on some conditions and rules.

        Parameters
        ----------
        word: str, input verb

        Returns
        -------
        str:
            output: if can decomposed verb with our rules else None
        """
        # All verb tenses
        decomposedـverb = self.verb_rule_checker(word)
        if decomposedـverb is not None:
            return decomposedـverb

        # special verb گرفتارم،گرفتاری، گرفتار است،....
        # TODO add verbs like است،هست،هستید
        if word in ["است"]:
            return word

        # **************افعال پیشوندی************
        # Todo: add this part to project
        # prefix1, candidate_list = self.remove_prefixes(word, self.affix_list["verb_prefix"])
        # if len(candidate_list) > 0:
        #     new_word = self.select_candidate(candidate_list)
        #     if new_word:
        #         tmp_pr = word[:-len(new_word)].strip().strip('\u200c')
        #         # new_word = self.convert_to_stem(new_word, word_pos='V')
        #         if new_word and new_word in self.verb_lexicon:
        #             if prefix1 in self.affix_list["verb_prefix_joint"]:
        #                 return prefix1 + new_word
        #             else:
        #                 return prefix1 + '\u200c' + new_word

        # todo : add this part to project
        # split  "می/نمی" from start of  all words
        # prefix1, candidate_list = self.remove_prefixes(word, self.affix_list["slang_verbs_prefix"])
        # print(candidate_list)
        # if len(candidate_list) > 0:
        #     new_word = self.select_candidate(candidate_list)
        #     if new_word:
        #         if new_word and new_word in self.noun_lexicon:
        #
        #                 return prefix1 + '\u200c' + new_word
        return None

    def noun_rule_checker_pre(self, input_word, affix_list):
        """
        lookup for prefixes in the input word.

        Parameters
        ----------
        input_word: str, input word that we should check its prefix.
        affix_list: list, potential prefixes that should lookup for them.

        Returns
        -------
        str:
            prefix: stem candidate: str,(if conditions satisfied and there is a prefix in the word)
        list:
            input_word: if can't find the prefix, will return input
        """
        # lookup for prefix of the noun
        prefix, candidate_list = self.remove_prefixes(input_word, affix_list)

        # check if there is a candidate and length of that candidate should be greater than 1
        if len(candidate_list) > 0 and prefix != '' and len(list(candidate_list)[0]) > 1:
            stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
            # check if the stem that finds it is in vocabulary or not?
            if stem_candidate:
                return prefix, stem_candidate
            else:
                # Maybe Word has a two-prefix, so we can continue on it.
                stem_candidate = self.select_candidate(candidate_list)
                return prefix, stem_candidate
        else:
            return [input_word]

    def noun_rule_checker_pos(self, input_word, affix_list):
        """
        lookup for postfixes in the input word.

        Parameters
        ----------
        input_word: str
            input word that we should check its postfix.
        affix_list: list
            potential postfixes that should lookup for them.

        Returns
        -------
        str:
            postfix: stem candidate: str,(if conditions satisfied and there is a postfix in the word)
        list:
            input_word: if can't find the postfix, will return input
        """

        # lookup for postfix of the noun
        postfix, candidate_list = self.remove_postfixes(input_word, affix_list)

        # check if there is a candidate and length of that candidate should be greater than 1
        if len(candidate_list) > 0 and postfix != '' and len(list(candidate_list)[0]) > 1:

            stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
            if stem_candidate:
                return postfix, stem_candidate
            else:
                # Maybe Word has a two-postfix, so we can continue on it.
                stem_candidate = self.select_candidate(candidate_list)
                return postfix, stem_candidate
        else:

            return [input_word]

    def noun_part_jointer(self, stem, suffix):
        """
        want to decide how to attach the suffixes and the stem together.

        Parameters
        ----------
        stem : str
            root of the word
        suffix : str
            list of suffix for a word
        Returns
        -------
        str:
            normalized version of word (Sticky version of the word)
        """

        ge_status = False  # boolean status to check whether there is گ
        text = ""

        if suffix["prefix"] != "":
            text = suffix["prefix"] if suffix["prefix"] in self.affix_list["prefix_joint"] else suffix[
                                                                                                    "prefix"] + self.separator_character

        text += stem

        if suffix["pos_ge"] != "":
            text += self.separator_character + suffix["pos_ge"]
            ge_status = True

        if suffix["pos_irreqular"] != "":
            if suffix["pos_irreqular"] in self.affix_list["postfix_joint"] + self.affix_list[
                "irregular_postfix_joint"] or ge_status:
                text += suffix["pos_irreqular"]
            else:
                text = text + self.separator_character + suffix["pos_irreqular"]

        if suffix["plural"] != "":
            if suffix["plural"] == "ا":
                suffix["plural"] = "ها"

            if suffix["plural"] in self.affix_list["postfix_joint"] or ge_status:
                text += suffix["plural"]
            else:
                text += self.separator_character + suffix["plural"]

        if suffix["pron"] != "":
            if (self.double_postfix_joint and suffix["plural"] != "") or suffix["pron"] in self.affix_list[
                "postfix_joint"] or ge_status:
                text += suffix["pron"]
            else:
                text += self.separator_character + suffix["pron"]

        if suffix["zame"] != "":
            text += " " + "رو"

        if suffix["he_chasban"] != "":
            pass

        return text

    def noun_decomposer(self, word):
        """
        Consider the prefix and postfix of the noun, then divide it according to the condition.

        Parameters
        ----------
        word: str
            input word that should be normalized

        Returns
        -------
        str:
            normalized word
        """

        # list of suffixes that we look up for them
        suffix = {"pron": "", "plural": "", "prefix": "", "pos_irreqular": "", "pos_ge": "", "zame": "",
                  "he_chasban": ""}

        # check for postfix with "گ" like: ستارگان
        try:
            new_word, suffix["pos_ge"] = self.postfix_g(word)

        except:
            new_word = word

        # Words and suffixes should be attached together
        if new_word in self.noun_lexicon and word != new_word:
            text = self.noun_part_jointer(new_word, suffix)
            return text

        # If there is a standard word based on the irregular postfixes, a normalized word will be returned
        try:
            suffix["pos_irreqular"], new_word = self.noun_rule_checker_pos(word,
                                                                           self.affix_list["irregular_postfix_all"])
        except:
            new_word = word

        # Words and suffixes should be attached together
        if new_word in self.noun_lexicon and word != new_word:
            text = self.noun_part_jointer(new_word, suffix)
            return text

        suffix = {"pron": "", "plural": "", "prefix": "", "pos_irreqular": "", "pos_ge": "", "zame": "",
                  "he_chasban": ""}
        # START chain analyze of word
        # check for "و" at the end of the word, e.x: کتابو
        try:
            suffix["zame"], new_word = self.noun_rule_checker_pos(word, self.affix_list["zame"])
        except:
            new_word = word

        # check for "ه" at the end of the word, e.x: ماشینه
        try:
            suffix["he_chasban"], new_word = self.noun_rule_checker_pos(new_word, self.affix_list["he_chasban"])
        except:
            new_word = new_word

        # check for pronoun of the word, e.x: ماشینم
        try:
            suffix["pron"], new_word = self.noun_rule_checker_pos(new_word, self.affix_list["prop_postfix_all"])
        except:
            new_word = new_word

        # check for plural form of the word, e.x: ماشینها
        try:
            suffix["plural"], new_word = self.noun_rule_checker_pos(new_word, self.affix_list["plural_postfix_all"])
        except:

            new_word = new_word
        # check for prefix of the word, e.x: پیشبینی

        try:
            suffix["prefix"], new_word = self.noun_rule_checker_pre(new_word, self.affix_list["prefix_all"])
        except:
            new_word = new_word
        # check for irregular postfix of the word, e.x: کتابسرا

        try:
            suffix["pos_irreqular"], new_word = self.noun_rule_checker_pos(new_word,
                                                                           self.affix_list["irregular_postfix_all"])
        except:
            new_word = new_word

        if new_word in self.noun_lexicon and word != new_word:
            text = self.noun_part_jointer(new_word, suffix)
            return text

        # if couldn't separate words in chain rules, in this section we just consider prefix and check if there is or not.
        # check for prefix of the word e.x: پیشبینی
        suffix = {"pron": "", "plural": "", "prefix": "", "pos_irreqular": "", "pos_ge": "", "zame": "",
                  "he_chasban": ""}
        try:
            suffix["prefix"], new_word = self.noun_rule_checker_pre(word, self.affix_list["prefix_all"])
        except:
            new_word = word
        # Words and suffixes should be attached together
        if new_word in self.noun_lexicon and word != new_word:
            text = self.noun_part_jointer(new_word, suffix)
            return text

    def convert_to_stem(self, word, word_pos=None):
        """
        find stem,postfix and prefix of words.

        Parameters
        ----------
        word: str, input words
        word_pos: Part of speech tag of word

        Returns
        -------
        stem of word with prefix and postfix of it
        """

        # If the word already exists in vocabulary(mini_lexicon), then it isn't combined
        if word in self.mini_lexicon:
            if word_pos is None or word_pos == 'N':
                return word

        # If the word already exists in verb vocabulary(verb_f2p_map), then it isn't combined
        elif word in self.verb_lexicon:
            if word_pos is None or word_pos == 'V':
                return word

        # find stem, postfix, and prefix of words.
        # we have 2 groups of words: 1. verbs 2. nouns,
        # each of them has separate rules.

        # ***************** VERB-Block *****************
        # Verify that the word is a composed verb
        if word_pos is None or word_pos == "V":
            decomposedـverb = self.verbs_decomposer(word)
            if decomposedـverb is not None:
                return decomposedـverb

        # ***************** NOUN-Block *****************
        # Verify that the word is a composed noun
        if word_pos is None or word_pos == "N":
            decomposedـnoun = self.noun_decomposer(word)
            if decomposedـnoun is not None:
                return decomposedـnoun

        return word
