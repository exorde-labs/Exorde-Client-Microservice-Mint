
import logging
from ftlangdetect import detect as lang_detect
from wtpsplit import WtP

from evaluate_token_count import evaluate_token_count
from exorde_data import Item, CreatedAt, Domain, Url, Content

wtp = WtP("wtp-canine-s-1l")

def split_in_sentences(string: str):
    sentences = []
    string_no_lb = string.replace("\n", " ")
    detected_language = lang_detect(string_no_lb, low_memory=False)
    try:
        try:
            sents = wtp.split(string, lang_code=detected_language["lang"])
        except:
            logging.info(
                f"WTP: could not split with lang: {detected_language}, trying with English..."
            )
            sents = wtp.split(string, lang_code="en")

        for doc in sents:
            sentences.append(doc)
    except Exception as e:
        logging.info(f"[Sentence splitter] error: {e}")
        sentences = []

    sentences = [x for x in sentences if x and len(x) > 5]
    return sentences


def aggregate_sents_into_paragraphs(
    sentences: list[str], chunk_size: int = 500
):
    paragraphs = []
    current_paragraph = []
    token_count = 0

    try:
        for sent in sentences:
            sent_ = str(sent).replace("\n", "")
            sent_tokens_count = int(evaluate_token_count(str(sent_)))
            # Check if adding the current sentence exceeds the maximum token count
            if token_count + sent_tokens_count > chunk_size:
                current_paragraph_str = " ".join(current_paragraph)
                paragraphs.append(current_paragraph_str)
                current_paragraph = []
                token_count = 0

            current_paragraph.append(sent_)
            token_count += sent_tokens_count

        # Add the last remaining paragraph
        if len(current_paragraph) > 0:
            current_paragraph_str = " ".join(current_paragraph)
            paragraphs.append(current_paragraph_str)

        logging.info(
            f"[Paragraph aggregator] Made {len(paragraphs)} paragraphs ({chunk_size} tokens long)"
        )
    except Exception as e:
        logging.info(f"[Paragraph aggregator] error: {e}")
        paragraphs = []

    paragraphs = [x for x in paragraphs if x and len(x) > 5]
    return paragraphs


def split_string_into_chunks(string: str, chunk_size: int):
    ## 1) Split main text in sentences
    sentences = split_in_sentences(string)
    ## 2) a) Recompose paragraphs from sentences
    ##    b) while keeping each paragram token count under "max_token_count"
    paragraphs = aggregate_sents_into_paragraphs(sentences, chunk_size)
    return paragraphs


def split_item(item: Item, max_token_count: int) -> list[Item]:
    if not item.content or len(str(item.content)) <= max_token_count:
        return [item]
    else:
        return [
            Item(
                content=Content(str(chunk)),
                author=item.author,
                created_at=CreatedAt(item.created_at),
                domain=Domain(item.domain),
                url=Url(item.url),
            )
            for chunk in split_string_into_chunks(
                str(item.content), max_token_count
            )
        ]


