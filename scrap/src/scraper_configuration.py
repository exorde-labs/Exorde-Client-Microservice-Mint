from dataclasses import dataclass
from typing import Dict, List, Union, Callable
from datetime import datetime, timedelta
import json
import aiohttp
import logging

PONDERATION_URL: str = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/modules_configuration_v2.json"

@dataclass
class ScraperConfiguration:
    enabled_modules: Dict[str, List[str]]
    module_list: list[str]
    generic_modules_parameters: Dict[str, Union[int, str, bool]]
    specific_modules_parameters: Dict[str, Dict[str, Union[int, str, bool]]]
    weights: Dict[str, float]
    lang_map: Dict[str, list]  # module_name as key
    new_keyword_alg: int # weight for #986


async def _get_scraper_configuration() -> ScraperConfiguration:
    async with aiohttp.ClientSession() as session:
        async with session.get(PONDERATION_URL) as response:
            response.raise_for_status()
            raw_data: str = await response.text()
            try:
                json_data = json.loads(raw_data)
            except Exception as error:
                logging.error(raw_data)
                raise error
            enabled_modules = json_data["enabled_modules"]
            generic_modules_parameters = json_data[
                "generic_modules_parameters"
            ]
            specific_modules_parameters = json_data[
                "specific_modules_parameters"
            ]
            weights = json_data["weights"]

            module_list: list[str] = [] # [owner/repo, ...]
            def transform_module_urls(modules):
                transformed_list = []
                for __key__, urls in modules.items():
                    for url in urls:
                        parts = url.split('/')
                        # Usually the owner is at the 4th position and the repo 
                        # at the 5th in the URL
                        owner_repo = parts[3] + '/' + parts[4]
                        transformed_list.append(owner_repo)
                return transformed_list
            module_list = transform_module_urls(enabled_modules) 

            logging.info(f"Lang Map is : {json_data['lang_map']}")

            return ScraperConfiguration(
                enabled_modules=enabled_modules,
                module_list=module_list,
                generic_modules_parameters=generic_modules_parameters,
                specific_modules_parameters=specific_modules_parameters,
                weights=weights,
                lang_map=json_data["lang_map"],
                new_keyword_alg=json_data["new_keyword_alg"],
            )

def scraper_configuration_geter() -> Callable:
    memoised = None
    last_call = datetime.now()

    async def get_scraper_configuration_wrapper() -> ScraperConfiguration:
        nonlocal memoised, last_call
        now = datetime.now()
        if not memoised or (now - last_call) > timedelta(minutes=1):
            last_call = datetime.now()
            memoised = await _get_scraper_configuration()
        return memoised

    return get_scraper_configuration_wrapper


get_scrapers_configuration: Callable = scraper_configuration_geter()