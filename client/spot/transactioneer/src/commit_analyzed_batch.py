
from ipfs import download_ipfs_file, upload_to_ipfs
from typing import Union

from spot_data import spot_data

from get_transaction_receipt import get_transaction_receipt
import logging


async def commit_analyzed_batch(processed_batch, app):
    logging.info("COMMIT_ANALYZED_BATCH")
    logging.info(processed_batch)
    try:
        cid: Union[str, None] = await upload_to_ipfs(processed_batch)
        logging.info(f"Uploaded : {cid}")
        if cid != None:
            post_upload_file: dict = await download_ipfs_file(cid)
            item_count = len(post_upload_file["items"])
            # check item count -> lever metric
            transaction_hash, previous_nonce = await spot_data(
                cid,
                item_count,
                app["static_configuration"]["worker_account"],
                app["live_configuration"],
                app["static_configuration"]["gas_cache"],
                app["static_configuration"]["contracts"],
                app["static_configuration"]["read_web3"],
                app["static_configuration"]["write_web3"],
                app["static_configuration"],
            )
            receipt = await get_transaction_receipt(
                transaction_hash, previous_nonce, app["static_configuration"]
            )
            logging.info("COMMIT OK")
            return transaction_hash, cid
    except Exception as e:
        logging.exception("An error occured while commiting a batch")
        raise e