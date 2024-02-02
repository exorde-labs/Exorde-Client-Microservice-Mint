
from aiohttp import web
from commit_analyzed_batch import commit_analyzed_batch
import logging
import os
import signal
import asyncio

def terminate(signal, frame):
    os._exit(0)

from get_static_configuration import get_static_configuration, StaticConfiguration
from get_live_configuration import get_live_configuration, LiveConfiguration


from aioprometheus.collectors import Counter

receipt_count = Counter(
    "transactioneer_receipt",
    "Amount of receipts received from the protocol"
)


from aioprometheus.collectors import REGISTRY
from aioprometheus.renderer import render

async def metrics(request):
    content, http_headers = render(REGISTRY, [request.headers.get("accept")])
    return web.Response(body=content, headers=http_headers)



TASKS = []
async def monitor_tasks():
    while True:
        for task in list(TASKS):
            if task.done():
                TASKS.remove(task)
                try:
                    # Handle task result or exception
                    await task 
                    # Process result if needed
                except Exception as e:
                    logging.exception("Task resulted in exception", exc_info=e)
        await asyncio.sleep(1)  # Sleep for some time before checking again



async def configuration_init(app):
    # arguments, live_configuration
    live_configuration: LiveConfiguration = await get_live_configuration()
    static_configuration: StaticConfiguration = await get_static_configuration(
            live_configuration, no_lab=True
    )
    app['static_configuration'] = static_configuration
    app['live_configuration'] = live_configuration

app = web.Application()
from models import Batch, BatchKindEnum

def log_callback(task):
    try:
        result = task.result()
        # Process result
    except Exception as e:
        logging.exception("An error occured in task")
        # Handle exception

app.router.add_get('/metrics', metrics)

async def create_task(items, app):
    global receipt_count
    logging.info("CREATING commit")
    try:
        await commit_analyzed_batch({"items": items, "kind": "SPOTTING"}, app)
        receipt_count.inc({})
    except:
        logging.exception("An Error occured commiting analyzed batch")
    logging.info("COMMIT OK")

async def make_transaction(request):
    global TASKS
    logging.info("NEW TRANSACTION REQUEST")
    items = await request.json()
    task = asyncio.create_task(create_task(items, request.app))
    task.add_done_callback(log_callback)
    logging.info("TRANSACTION TASK CREATED")
    TASKS.append(task)
    return web.Response(text='received')

async def healthcheck(__request__):
    return web.Response(status=200)

app.router.add_post('/commit', make_transaction)
app.router.add_get('/', healthcheck)

async def start_background_tasks(app):
    app['monitor_task'] = asyncio.create_task(monitor_tasks())

def start_transactioneer():
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    port = int(os.environ.get("PORT", "7991"))
    logging.info(f"Hello World! I'm TRANSACTIONEER running on {port}")
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)

    logging.info(f"Starting server on {port}")
    app.on_startup.append(configuration_init)
    app.on_startup.append(start_background_tasks)
    try:
        asyncio.run(web._run_app(app, port=port, handle_signals=True))
    except KeyboardInterrupt:
        os._exit(0)


if __name__ == '__main__':
    start_transactioneer()
