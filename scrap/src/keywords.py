import logging, os, json, aiohttp, time, re, random, asyncio

from typing import Optional, Dict, Tuple
from scraper_configuration import ScraperConfiguration

from aioprometheus.collectors import Counter

from opentelemetry import trace
from opentelemetry.trace.status import Status
from opentelemetry.trace import StatusCode



FALLBACK_DEFAULT_LIST = [
    "bitcoin",
    "ethereum",
    "eth",
    "btc",
    "usdt",
    "usdc",
    "stablecoin",
    "defi",
    "finance",
    "liquidity",
    "token",
    "economy",
    "markets",
    "stocks",
    "crisis",
]
KEYWORDS_URL = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/keywords.txt"
JSON_FILE_PATH = "keywords.json"
KEYWORDS_UPDATE_INTERVAL = 5 * 60  # 5 minutes

## READ KEYWORDS FROM SOURCE OF TRUTH
async def fetch_keywords(keywords_raw_url) -> str:
    for i in range(0, 10):
        await asyncio.sleep(i * i)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    keywords_raw_url, timeout=10
                ) as response:
                    return await response.text()
        except Exception as e:
            logging.info(
                "[KEYWORDS] Failed to download keywords.txt from Github repo exorde-labs/TestnetProtocol: %s",
                e,
            )
    raise ValueError(
        "[KEYWORDS] Failed to download keywords.txt from Github repo exorde-labs/TestnetProtocol: %s"
    )


## CACHING MECHANISM
# save keywords to a local file, at root directory, alongside the timestamp of the update
def save_keywords_to_json(keywords):
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as json_file:
        json.dump(
            {"last_update_ts": int(time.time()), "keywords": keywords},
            json_file,
            ensure_ascii=False,
        )


# load keywords from local file, if exists
def load_keywords_from_json():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            return data["keywords"]
    return None


#######################################################################################################
def filter_strings(str_list):
    # Step 1: strip each string and remove '\n', '\r' characters
    step1 = [s.strip().replace("\n", "").replace("\r", "") for s in str_list]
    # Step 2: remove '\\uXXXX' characters
    step2 = [re.sub(r"\\u[\da-fA-F]{4}", "", s) for s in step1]
    step3 = [s for s in step2 if s]

    return step3


#######################################################################################################
async def get_keywords():
    # Checking if JSON file exists.
    if os.path.exists(JSON_FILE_PATH):
        try:
            # Attempting to read the JSON file.
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                last_update_ts = data.get("last_update_ts", 0)
                ts = int(time.time())
                # If last update was less than 5 minutes ago, return the stored keywords
                if ts - last_update_ts < KEYWORDS_UPDATE_INTERVAL:
                    return data.get("keywords", [])
        except Exception as e:
            logging.info(f"[KEYWORDS] Error during reading the JSON file: {e}")

    # If execution reaches here, it means either JSON file does not exist
    # or the last update was more than 5 minutes ago. So, we attempt to fetch the keywords from the URL.
    try:
        keywords_txt = await fetch_keywords(KEYWORDS_URL)

        # Checking if fetch_keywords returned None.
        if keywords_txt is None:
            raise Exception("fetch_keywords returned None")

        keywords = keywords_txt.replace("\n", "").split(",")
        keywords = filter_strings(keywords)
        save_keywords_to_json(keywords)
        return keywords
    except Exception as e:
        logging.info(
            f"[KEYWORDS] Error during the processing of the keywords list: {e}"
        )

    # If execution reaches here, it means either fetch_keywords returned None
    # or there was an error during processing the keywords. 
    # Attempt to return the keywords from the JSON file, if it exists.
    if os.path.exists(JSON_FILE_PATH):
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                return data.get("keywords", [])
        except Exception as e:
            logging.info(f"[KEYWORDS] Error during reading the JSON file: {e}")
    # If execution reaches here, it means either JSON file does not exist
    # or there was an error during reading the JSON file.
    # Return the fallback default list.
    logging.info(f"[KEYWORDS] Returning default fallback list")
    return FALLBACK_DEFAULT_LIST


def create_topic_lang_fetcher(refresh_frequency: int = 3600):
    url: str = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/topic_lang_keywords.json"
    cached_data: Optional[Dict[str, dict[str, list[str]]]] = None
    last_fetch_time: float = 0

    async def fetch_data() -> dict[str, dict[str, list[str]]]:
        """
        {
            <topic>: {
                <lang-a>: ["Foo"],
                <lang-b>: []
            }
        }
        some langs can have empty lists
        """
        nonlocal cached_data, last_fetch_time
        current_time: float = time.time()

        # Check if data should be refreshed
        if (
            cached_data is None
            or current_time - last_fetch_time >= refresh_frequency
        ):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        data = json.loads(await response.text())
                        cached_data = data
                        last_fetch_time = current_time
                        logging.info(
                            "Data refreshed at: %s",
                            time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime()
                            ),
                        )
            except Exception as e:
                logging.error("Error fetching data: %s", str(e))
        if not cached_data:
            raise Exception("Could not download topics")
        else:
            return cached_data

    return fetch_data


topic_lang_fetcher = create_topic_lang_fetcher()


async def choose_translated_keyword(
    scrap_module_name: str, scraper_configuration: ScraperConfiguration
):
    """
    New keyword_choose alg takes into account the module language and translated
    keywords

    translations are specified in topics and modules have different language
    capabilities
    """

    """retrieve the topic lang data"""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("choose_translated_keyword") as choose_translated_keyword_span:
        try:
            topic_lang: dict[str, dict[str, list[str]]] = await topic_lang_fetcher()
            """Get a random topic"""
            # retrieve list of topics
            topics: list[str] = list(topic_lang.keys())
            assert len(topics), "Retrieved topics are empty"
            choosed_topic = random.choice(topics)
        except:
            logging.exception(
                "while retrieving topic-lang in choose_translated_keyword, using fall-back"
            )
            return random.choice(FALLBACK_DEFAULT_LIST)
        try:
            """
            retrieve available languages for the specified topic,  filter out topics
            with empty translations 
            """
            topic_languages = [
                lang for lang in list(
                    topic_lang[choosed_topic].keys()
                ) if len(topic_lang[choosed_topic][lang])
            ]
            assert len(topic_languages), "Topic has no translation"

            """retrieve available languages for the specified scrap_module_path"""
            # lang_map[module_hash]
            module_languages = scraper_configuration.lang_map[scrap_module_name]
            assert len(module_languages), "Scraper module does not support topic-lang"

            if module_languages == ["all"]:
                """
                module language compat can be set to `all` in which case every 
                language is considered
                """
                intercompatible_languages = topic_languages
            else:
                """Determin languages that are scraper compatible and translated"""
                intercompatible_languages = [
                    lang for lang in topic_languages if lang in module_languages
                ]

            # if there is no match we fall back using the topic
            assert len(intercompatible_languages), "No language intercompatible"

            choose_translated_keyword_span.set_status(StatusCode.OK)
            # else we have a translated keyword by choosing an item in the list
            logging.info(f"intercompatible_languages: {intercompatible_languages}")
            choosen_language = random.choice(intercompatible_languages)
            choosen_translated_keyword = random.choice(topic_lang[choosed_topic][choosen_language])
            return choosen_translated_keyword
        except (KeyError, AssertionError) as e:
            choose_translated_keyword_span.set_status(Status(StatusCode.ERROR))
            choose_translated_keyword_span.record_exception(e)
            logging.exception(
                "Error while using topic-lang algorithm, using topic"
            )
            # if there is no match we fall back using the topic
            return choosed_topic


async def default_choose_keyword():
    keywords_: list[str] = await get_keywords()
    selected_keyword: str = random.choice(keywords_)
    return selected_keyword


"""
Notes:
    - there is currently two formats of keywords used which are feature-flipped
    and used interchangably ; both are being currently researched on
"""
keyword_counter = Counter("keyword", "keyword used to scrap")

async def choose_keyword(
    scrap_module_path: str,
    scraper_configuration: ScraperConfiguration,
) -> Tuple[str, str]:
    """Feature-flipped with a threshold cursor"""
    # cursor
    algorithm_choose_cursor = scraper_configuration.new_keyword_alg
    # number generation
    random_number = random.randint(0, 99)
    alg = None
    result = None
    """
    a cursor at 80 would give it 80% chance of beeing choosen
    
    new algorithm is choosen if the random number is bellow the cursor

    | . . . . c . . |

    """
    logging.debug(f" random_number: {random_number} ; algorithm_choose_cursor: {algorithm_choose_cursor}")
    random_number = 1
    if random_number <= algorithm_choose_cursor:
        try:
            result = await choose_translated_keyword(
                scrap_module_path, scraper_configuration
            )
            alg = 'new'
        except:
            logging.exception("An unhandled error occured in choose_translated_keyword")
            result = await default_choose_keyword()
            alg = 'old'
    else:
        result = await default_choose_keyword()
        alg = 'old'
    logging.info(f"choosed new keyword '{result}' (alg: {alg})")
    keyword_counter.inc({"keyword": result, "alg": alg})
    return result