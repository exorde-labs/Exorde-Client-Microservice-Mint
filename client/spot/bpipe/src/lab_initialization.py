import requests
import spacy
import torch
from transformers import pipeline
from argostranslate import translate as _translate
import logging


def lab_initialization():
    device = torch.cuda.current_device() if torch.cuda.is_available() else -1
    mappings = {
        "Gender": {0: "Female", 1: "Male"},
        "Age": {0: "<20", 1: "20<30", 2: "30<40", 3: ">=40"},
        # "HateSpeech": {0: "Hate speech", 1: "Offensive", 2: "None"},
    }
    try:
        nlp = spacy.load("en_core_web_trf")
    except Exception as err:
        logging.exception("Could not load en_core_web_trf")
        raise err
    installed_languages = _translate.get_installed_languages()
    return {
        "device": device, # bpipe & upipe
        "mappings": mappings, #bpipe
        "nlp": nlp, #bpipe
        "max_depth": 2,
        "remove_stopwords": False,
    }
