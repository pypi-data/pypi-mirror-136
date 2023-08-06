from spacy_loader import nlp
with nlp.select_pipes(enable=["char_normalizer","affix2norm"]):
    print(nlp("کتابتون رو به من میدهید؟"))
nlp.remove_pipe("spell_checker")
print(nlp.pipeline)
