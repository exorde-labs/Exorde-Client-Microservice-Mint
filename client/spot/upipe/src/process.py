import json, logging
from preprocess import preprocess
from translate import translate
from extract_keywords import extract_keywords
from zero_shot import zero_shot
from exorde_data import (
    Classification,
    Translation,
    Keywords,
    Processed,
    Item,
)
from evaluate_token_count import evaluate_token_count

from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode

class TooBigError(Exception):
    pass

def process(
    item: Item, lab_configuration, max_depth_classification
) -> Processed:
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        "evaluate_token_count"
    ) as evaluate_token_count_span:
        token_count = evaluate_token_count(item['content'])
        evaluate_token_count_span.set_status(StatusCode.OK)
        if token_count >= lab_configuration["max_token_count"]:
            logging.info(".................................................")
            logging.info("\tItem too big, skipping")
            logging.info(
                f"\t\t->Item token count = {evaluate_token_count(item['content'])}"
            )
            raise TooBigError
    try:
        with tracer.start_as_current_span("preprocess_item") as preprocess_span:
            try:
                item = preprocess(item, False)
                preprocess_span.set_status(StatusCode.OK)
            except Exception as err:
                preprocess_span.set_status(Status(StatusCode.ERROR, str(err)))
                logging.error("An error occured pre-processing an item")
                logging.error(err)
                logging.error(json.dumps(item, indent=4))
                raise err

        with tracer.start_as_current_span(
            "translate_item"
        ) as translation_span:
            try:
                translation: Translation = translate(
                    item, lab_configuration["installed_languages"]
                )
                translation_span.set_status(StatusCode.OK)
                if translation.translation == "":
                    raise ValueError("No content to work with")
            except Exception as err:
                logging.error("An error occured translating an item")
                translation_span.set_status(Status(StatusCode.ERROR, str(err)))
                logging.error(err)
                logging.error(json.dumps(item, indent=4))
                raise err

        with tracer.start_as_current_span(
            "keyword_extract_item"
        ) as keyword_extract_span:
            try:
                top_keywords: Keywords = extract_keywords(translation)
                keyword_extract_span.set_status(StatusCode.OK)
            except Exception as err:
                keyword_extract_span.set_status(
                    Status(StatusCode.ERROR, str(err))
                )
                logging.error(
                    "An error occured populating keywords for an item"
                )
                logging.error(err)
                logging.error(json.dumps(translation, indent=4))
                raise err

        with tracer.start_as_current_span(
            "item_classification"
        ) as item_classification_span:
            try:
                classification: Classification = zero_shot(
                    translation,
                    lab_configuration,
                    max_depth=max_depth_classification,
                )
                item_classification_span.set_status(StatusCode.OK)
            except Exception as err:
                item_classification_span.set_status(
                    Status(StatusCode.ERROR, str(err))
                )
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
