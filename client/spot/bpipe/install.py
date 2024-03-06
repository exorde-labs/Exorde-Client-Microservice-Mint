"""
The install script is part of the Dockerfile and is intented to pre-download
additional model dependencies that would have been downloaded at run-time.
"""

from huggingface_hub import hf_hub_download
from wtpsplit import WtP
from typing import cast
import os
from transformers import AutoModel, AutoTokenizer
from argostranslate import package

models = [
    "SamLowe/roberta-base-go_emotions",
    "cardiffnlp/twitter-roberta-base-irony",
    "salesken/query_wellformedness_score",
    "marieke93/MiniLM-evidence-types",
    "alimazhar-110/website_classification",
    "bert-large-uncased",
    "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
    "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
]

def install_hugging_face_models(models):
    for model in models:
        print(f"Install {model}")
        __tokenizer__ = AutoTokenizer.from_pretrained(model)
        model = AutoModel.from_pretrained(model)

cache_dir = os.path.join(
    os.getenv('HOME', '/root'), '.cache', 'huggingface', 'hub'
)

install_hugging_face_models(models)


print("install emoji_lexicon")
emoji_lexicon = hf_hub_download(
    repo_id="ExordeLabs/SentimentDetection",
    filename="emoji_unic_lexicon.json",
    cache_dir=cache_dir
)
print(f"emoji lexicon downloaded : {emoji_lexicon}")
print("install loughran_dict")
loughran_dict = hf_hub_download(
    repo_id="ExordeLabs/SentimentDetection",
    filename="loughran_dict.json",
    cache_dir=cache_dir
)
