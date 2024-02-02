#! python3.10

from wtpsplit import WtP # wtpsplit/issues/10

import logging, os

import asyncio
import signal
from aioprometheus.collectors import REGISTRY
from aioprometheus.renderer import render
from aiohttp import web, ClientSession
import time

app = web.Application()

from aioprometheus.collectors import Counter, Histogram

receive_counter = Counter(
    "processor_reception", 
    "Number of 'receive' calls by item processor"
)
too_big_counter = Counter(
    "processor_too_big", 
    "Number of items that are marked as too big by processor"
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

def terminate(signal, frame):
    os._exit(0)

async def healthcheck(__request__):
    return web.Response(status=200)

async def metrics(request):
    content, http_headers = render(REGISTRY, [request.headers.get("accept")])
    return web.Response(body=content, headers=http_headers)

from exorde_data import Item
from process import process, TooBigError

from get_static_configuration import get_static_configuration, StaticConfiguration
from get_live_configuration import get_live_configuration, LiveConfiguration

from split_item import split_item
from concurrent.futures import ThreadPoolExecutor

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
                    processed_item = await asyncio.wait_for(
                        loop.run_in_executor(
                            executor,
                            process,
                            current_item,
                            app["static_configuration"]["lab_configuration"],
                            app["live_configuration"]["max_depth"]
                        ),
                        timeout
                    )
                    logging.info(
                        f"PROCESS OK - ADDING TO BATCH : {processed_item}"
                    )
                    async with ClientSession() as session:
                        target = os.getenv('batch_target')
                        assert target
                        async with session.post(target, json=processed_item):
                            # You can process the response here if needed
                            logging.info("PROCESSED ITEM SENT")
                    # send to batch_processor
                except asyncio.TimeoutError:
                    logging.error("Processing timeoud out")
                except TooBigError:
                    too_big_counter.inc({})
                    splitted: list[Item] = split_item(
                        current_item,
                        app["live_configuration"]["max_token_count"]
                    )
                    process_buffer.extend(splitted)
                except AssertionError:
                    logging.info("No batch_target configured")

    async def process_external(item: Item, app) -> None:
        nonlocal process_buffer
        process_buffer.append(item)
        if semaphore.locked():
            logging.info("Another item added to process queue")
        else:
            await process_internal(app)

    return process_external
item_processor = create_processor()


from exorde_data import CreatedAt, Content, Domain, Url, Title

# Summary, Picture, Author, ExternalId, ExternalParentId,

async def receive_item(request):
    raw_item = await request.json()
    receive_counter.inc({"host": request.headers.get("Host")})
    try:
        item: Item = Item(
            created_at=CreatedAt(raw_item['created_at']),
            title=Title(raw_item.get('title', '')),
            content=Content(raw_item['content']),
            domain=Domain(raw_item['domain']),
            url=Url(raw_item['url'])
        )
        await item_processor(item, request.app)
        # prep
        logging.info(item)
        # send
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
    port = int(os.environ.get("PORT", "7998"))
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
