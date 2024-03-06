"""
The install script is part of the Dockerfile and is intented to pre-download
additional model dependencies that would have been downloaded at run-time.
"""

from wtpsplit import WtP
from typing import cast
import logging
import os
from transformers import AutoModel, AutoTokenizer
from argostranslate import package
import nltk
from sentence_transformers import SentenceTransformer
nltk.download('punkt')

models = [
    "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",

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
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def is_english_target(s):
    return '→ English' in s

langs_to_exclude_from_preinstall = ["Catalan", "Esperanto"]

def is_to_exclude(s):
    for lang in langs_to_exclude_from_preinstall:
        if lang in s:
            return True
    return False

package.update_package_index()
available_packages = package.get_available_packages()
length = len(available_packages)
i = 0
installed_packages = 0
for pkg in available_packages:
    i += 1
    
    if( is_english_target(str(pkg)) and not is_to_exclude(str(pkg)) ):
        print(
            f" - installing translation module ({i}/{length}) : ({str(pkg)})"
        )

        # cast used until this is merged https://github.com/argosopentech/argos-translate/pull/329
        package.install_from_path(
            cast(package.AvailablePackage, pkg).download()
        )
        installed_packages += 1
logging.info(f"Installed Argos Lang packages: {str(installed_packages)}")

wtp = WtP("wtp-canine-s-1l")


