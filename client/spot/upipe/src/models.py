
from madtypes import MadType
from exorde_data import Item

from typing import Optional


class Translated(str, metaclass=MadType):
    description = "The content translated in English language"
    annotation = str


class Language(str, metaclass=MadType):
    description = (
        "ISO639-1 language code that consists of two lowercase letters"
    )
    annotation = str


class Classification(dict, metaclass=MadType):
    description = "label and score of zero_shot"
    score: float
    label: str


class CalmTranslation(dict):
    """Result of argos translate"""

    language: Optional[Language]  # uses content or title
    translation: Translated


class Translation(CalmTranslation, metaclass=MadType):
    pass


class Keywords(list, metaclass=MadType):
    description = "The main keywords extracted from the content field"
    annotation = list[str]


class Processed(dict, metaclass=MadType):
    translation: Translation
    top_keywords: Keywords
    classification: Classification
    item: Item
