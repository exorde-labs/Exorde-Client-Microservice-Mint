
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
