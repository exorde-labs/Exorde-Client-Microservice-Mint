import json
from typing import Callable, Coroutine
import logging
from functools import wraps
import aiohttp

from typing import Optional

class LiveConfiguration(dict):
    """
    Configuration is not a MadType because we do not want to break the
    configuration instantiation if a key is not defined in the python
    code.
    ! it therfor requires a manual checking ; what happens when the user
    is unable to reach the configuration but the protocol is still online ?
    """

    remote_kill: bool
    online: bool
    batch_size: int
    last_info: Optional[str]
    worker_version: Optional[str]
    protocol_version: Optional[str]
    expiration_delta: Optional[int]  # data freshness
    target: Optional[str]
    default_gas_price: Optional[int]
    default_gas_amount: Optional[int]
    gas_cap_min: Optional[int]
    inter_spot_delay_seconds: int
    last_notification: str



def logic(implementation: Callable) -> Callable:
    @wraps(implementation)
    async def call() -> LiveConfiguration:
        try:
            return await implementation()
        except:
            """If configuration fails we should stop the process"""
            logging.exception("An error occured retrieving the configuration.")
            return LiveConfiguration(
                online=False, batch_size=0, inter_spot_delay_seconds=60
            )

    return call


async def implementation() -> LiveConfiguration:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/runtime.json"
        ) as response:
            data = json.loads(await response.text())
            return LiveConfiguration(**data)


get_live_configuration: Callable[
    [], Coroutine[None, None, LiveConfiguration]
] = logic(implementation)
