import json, logging
from preprocess import preprocess
from translate import translate
from extract_keywords import extract_keywords
from zero_shot import zero_shot
from models import (
    Classification,
    Translation,
    Keywords,
    Processed,
    Item,
)
from evaluate_token_count import evaluate_token_count


class TooBigError(Exception):
    pass


def process(
    item: Item, lab_configuration, max_depth_classification
) -> Processed:
    if evaluate_token_count(item['content']) >= lab_configuration["max_token_count"]:
        logging.info(".............................................................................................")
        logging.info("\tItem too big, skipping")
        logging.info(f"\t\t->Item token count = {evaluate_token_count(item['content'])}")

        raise TooBigError
    try:
        try:
            item = preprocess(item, False)
        except Exception as err:
            logging.error("An error occured pre-processing an item")
            logging.error(err)
            logging.error(json.dumps(item, indent=4))
            raise err

        try:
            translation: Translation = translate(
                item, lab_configuration["installed_languages"]
            )
            if translation.translation == "":
                raise ValueError("No content to work with")
        except Exception as err:
            logging.error("An error occured translating an item")
            logging.error(err)
            logging.error(json.dumps(item, indent=4))
            raise err

        try:
            top_keywords: Keywords = extract_keywords(translation)
        except Exception as err:
            logging.error("An error occured populating keywords for an item")
            logging.error(err)
            logging.error(json.dumps(translation, indent=4))
            raise err
        try:
            classification: Classification = zero_shot(
                translation,
                lab_configuration,
                max_depth=max_depth_classification,
            )
        except Exception as err:
            logging.error("An error occured classifying an item")
            logging.error(err)
            logging.error(json.dumps(translation, indent=4))
            raise err
        logging.info(translation)
        return Processed(
            item=item,
            translation=translation,
            top_keywords=top_keywords,
            classification=classification,
        )
    except Exception as err:
        raise (err)
