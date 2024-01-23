#! python3.10

from wtpsplit import WtP # wtpsplit/issues/10

import logging, os

import asyncio
import signal
from aioprometheus.collectors import REGISTRY
from aioprometheus.renderer import render
from aiohttp import web
import time

app = web.Application()

from aioprometheus.collectors import Counter, Histogram, Gauge

receive_counter = Counter(
    "reception", 
    "Number of 'receive' calls by spotting"
)
too_big_counter = Counter(
    "too_big", 
    "Number of items that are marked as too big"
)
process_histogram = Histogram(
    "process_execution_duration_seconds", 
    "Duration of 'process' in seconds", 
    buckets=[0, 1, 2, 3, 4, 5, 10, 15, 20]
)
successful_process = Counter(
    "process_successful", 
    "Amount of successfully processed items"
)
process_error = Counter(
    "process_error", 
    "Amount of errored process"
)
batch_size_gauge = Gauge(
    "batch_size", 
    "Current batch size"
)
batch_buffer_size_gauge = Gauge(
    "batch_buffer_size", 
    "Amount of batches in queue"
)
receipt_count = Counter(
    "spotting_receipt",
    "Amount of spotting receipts"
)

def terminate(signal, frame):
    os._exit(0)

async def healthcheck(__request__):
    return web.Response(status=200)

async def metrics(request):
    content, http_headers = render(REGISTRY, [request.headers.get("accept")])
    return web.Response(body=content, headers=http_headers)

"""
-
a. Receive data
b. Process_data
    -> expect TooBigError
        -> split item
            for e in splitted:
                append e
c. Add to batch

-
a. On batch ready
b. Process_batch
c. Upload_to_ipfs
d. Download ipfs file
e. If count != 0 : continue
f. Transaction
g. Get receipt 
"""

from exorde_data import Item
from models import StaticConfiguration
from process import process, TooBigError, Processed

from get_static_configuration import get_static_configuration
from get_live_configuration import get_live_configuration, LiveConfiguration

from split_item import split_item
from concurrent.futures import ThreadPoolExecutor


def batch_reached_mature_size(batch) -> bool:
    logging.info(f"BATCH SIZE IS {len(batch)}")
    batch_size_gauge.set({}, len(batch))
    if len(batch) >= 20:
        return True
    return False

from process_batch import process_batch
from commit_analyzed_batch import commit_analyzed_batch

def create_batch_processor():
    # Initialize semaphore and batch buffer
    semaphore = asyncio.Semaphore(1)
    batch_buffer = []

    async def process_batch_internal(batch, app) -> None:
        nonlocal semaphore, batch_buffer
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()

        # Process batches from the buffer
        while batch_buffer:
            current_batch = batch_buffer.pop(0)
            async with semaphore:
                try:
                    timeout = 150  # Set your desired timeout in seconds
                    logging.info("RUNNING BATCH PROCESSOR")
                    result = await asyncio.wait_for(
                        loop.run_in_executor(
                            executor, 
                            process_batch, 
                            current_batch, 
                            app["static_configuration"]
                        ),
                        timeout
                    )
                    logging.info("BATCH PROCESSOR COMPLETE")
                    # Handle the processed result
                    logging.info("COMMITING")
                    await commit_analyzed_batch(result, app, receipt_count)
                    logging.info("COMMIT OK")
                except asyncio.TimeoutError:
                    logging.error("Processing timed out for batch")
                    # Handle the timeout case as needed

    async def process_batch_external(batch, app) -> None:
        nonlocal batch_buffer
        # Add new batch to the buffer
        batch_buffer.append(batch)
        batch_buffer_size_gauge.set({}, len(batch_buffer))
        # Trigger internal processing if not already running
        if semaphore.locked():
            logging.info(
                "Another batch processing is in progress. Batch added to the buffer."
            )
        else:
            await process_batch_internal(batch, app)

    return process_batch_external
trigger_batch_process = create_batch_processor()


BATCH: list[Processed] = []
async def run_batch_completion_trigger(app):
    """
    Checks wether the BATCH should be sent to processing and runs it if it does
    """
    global BATCH, receipt_count
    if batch_reached_mature_size(BATCH):
        logging.info("BATCH_REACHED_MAT_SIZE")
        current_batch = [(i + 1, item) for i, item in enumerate(BATCH.copy())]
        BATCH = []
        await trigger_batch_process(current_batch, app)

class Busy(Exception):
    """Thread Queue is busy handeling another item"""

    def __init__(self, message="Thread queue is busy handeling another item"""):
        self.message = message
        super().__init__(self.message)


def create_processor():
    semaphore = asyncio.Semaphore(1)
    process_buffer = []

    async def process_internal(app) -> None:
        global BATCH
        nonlocal semaphore, process_buffer
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()

#        start = time.time()
#        end = time.time()
#        process_histogram.observe({"time": "static"}, end - start)
#        successful_process.inc({})

        while process_buffer:
            current_item = process_buffer.pop(0)
            async with semaphore:
                try:
                    timeout = 60
                    logging.info("PROCESS START")
                    result = await asyncio.wait_for(
                        loop.run_in_executor(
                            executor,
                            process,
                            current_item,
                            app["static_configuration"]["lab_configuration"],
                            app["live_configuration"]["max_depth"]
                        ),
                        timeout
                    )
                    logging.info("PROCESS OK - ADDING TO BATCH")
                    BATCH.append(result)
                    await run_batch_completion_trigger(app)
                except asyncio.TimeoutError:
                    logging.error("Processing timeoud out")
                except TooBigError:
                    too_big_counter.inc({})
                    splitted: list[Item] = split_item(
                        current_item,
                        app["live_configuration"]["max_token_count"]
                    )
                    process_buffer.extend(splitted)

    async def process_external(item: Item, app) -> None:
        nonlocal process_buffer
        process_buffer.append(item)
        if semaphore.locked():
            logging.info("Another item added to process queue")
        else:
            await process_internal(app)

    return process_external
item_processor = create_processor()

async def push_item(item: Item, app):
    """Interface to push new items into the processing batch"""
    await item_processor(item, app)
    # BATCH is manipulated by the item_processor


from exorde_data import CreatedAt, Content, Domain, Url, Title

# Summary, Picture, Author, ExternalId, ExternalParentId,

async def receive_item(request):
    raw_item = await request.json()
    receive_counter.inc({"host": request.headers.get("Host")})
    try:
        item: Item = Item(
            created_at=CreatedAt(raw_item['created_at']),
            title=Title(raw_item['title']),
            content=Content(raw_item['content']),
            domain=Domain(raw_item['domain']),
            url=Url(raw_item['url'])
        )
        logging.info(item)
        await push_item(item, request.app)
    except:
        logging.exception("An error occured asserting an item structure")
        logging.debug(raw_item)
    return web.Response(text="received")

app.router.add_post('/', receive_item)
app.router.add_get('/', healthcheck)
app.router.add_get('/metrics', metrics)

async def configuration_init(app):
    # arguments, live_configuration
    live_configuration: LiveConfiguration = await get_live_configuration()
    static_configuration: StaticConfiguration = await get_static_configuration(
        live_configuration
    )
    app['static_configuration'] = static_configuration
    app['live_configuration'] = live_configuration


def start_spotter():
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    port = int(os.environ.get("PORT", "7999"))
    logging.info(f"Hello World! I'm running on {port}")
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)

    logging.info(f"Starting server on {port}")
    app.on_startup.append(configuration_init)
    try:
        asyncio.run(web._run_app(app, port=port, handle_signals=True))
    except KeyboardInterrupt:
        os._exit(0)


if __name__ == '__main__':
    start_spotter()
