
from aiohttp import web, ClientSession
import logging
import os
import signal
import asyncio
import time
import json

def terminate(signal, frame):
    os._exit(0)

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.status import Status
from opentelemetry.trace import StatusCode
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider

from aioprometheus.collectors import Counter, Gauge

from exorde_data.get_live_configuration import get_live_configuration, LiveConfiguration
from commit_analyzed_batch import commit_analyzed_batch
from get_web3_configuration import get_web3_configuration, Web3Configuration
from claim_master import claim_master
from faucet import faucet

receipt_count = Counter(
    "transactioneer_receipt",
    "Amount of receipts received from the protocol"
)
receipt_count_populated = Counter(
    "transactioneer_receipt_populated",
    "Amount of receipts received from the protocol"
)
sent_items_count = Counter(
    "sent_items_count",
    "Amount of items commited to the network"
)
leaderboard_score = Gauge(
    "leaderboard",
    "Exorde leaderboard score"
)
leaderboard_rank = Gauge(
    "leaderboard_rank",
    "Exorde leaderboard rank"
)


from aioprometheus.collectors import REGISTRY
from aioprometheus.renderer import render

def setup_tracing():
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "transactioneer"
    })
    trace_provider = TracerProvider(resource=resource)
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(trace_provider)

async def metrics(request):
    content, http_headers = render(REGISTRY, [request.headers.get("accept")])
    return web.Response(body=content, headers=http_headers)


async def get_leaderboard(app):
    logging.info("Retrieving leaderboard")
    async with ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/leaderboard.json"
        ) as response:
            data = await response.text()
            data = json.loads(data)
            for rank, addr in enumerate(data, start=1):
                if data[addr] != 0:
                    leaderboard_score.set(
                        { "address": addr, "rank": rank },
                        data[addr]
                    )
                    leaderboard_rank.set(
                        { "address": addr, "rep": data[addr] }, rank
                    )
            logging.info("Leaderboard updated")

TASKS = []
async def monitor_tasks(app):
    last_leaderboard_fetch = time.time()
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

        # Check if it's time to fetch the leaderboard
        if time.time() - last_leaderboard_fetch >= 300:  # 300 seconds = 5 min
            try:
                await get_leaderboard(app)
            except:
                logging.exception(
                    "An error occured while retrieving leaderboard"
                )
            
            last_leaderboard_fetch = time.time()

        await asyncio.sleep(1)  # Sleep for some time before checking again


async def configuration_init(app):
    # arguments, live_configuration
    live_configuration: LiveConfiguration = await get_live_configuration()
    web3_configuration: Web3Configuration = await get_web3_configuration(
        live_configuration
    )
    app['web3_configuration'] = web3_configuration
    app['live_configuration'] = live_configuration

app = web.Application()

def log_callback(task):
    try:
        result = task.result()
        # Process result
    except Exception as e:
        logging.exception("An error occured in task")
        # Handle exception

app.router.add_get('/metrics', metrics)

async def create_task(items, app):
    tracer = trace.get_tracer(__name__)
    global receipt_count, sent_items_count
    logging.info(f"CREATING commit with {len(items)} items to push")
    for item in items:
        sent_items_count.inc({})
        logging.info("===")
        logging.info(f"{item}")
        for key in item:
            logging.info(f"- has {key}")
        logging.info('.item has...')
        for key in item['item']:
            logging.info(f'\t-{key}')
        logging.info("===")
    with tracer.start_as_current_span("commit_analyzed_batch") as commit_analyzed_batch_span:
        try:
            transaction_hash, cid = await commit_analyzed_batch(
                {"items": items, "kind": "SPOTTING"}, app
            )
            commit_analyzed_batch_span.set_status(StatusCode.OK)
            commit_analyzed_batch_span.set_attribute("CID", cid)
            commit_analyzed_batch_span.set_attribute(
                "TX", transaction_hash.hex()
            )
            receipt_count.inc({})
            receipt_count_populated.inc(
                { "CID": cid, "TX": transaction_hash.hex() }
            )
            logging.info("COMMIT OK")
        except Exception as e:
            logging.info("COMMIT FAILED")
            logging.exception("An Error occured commiting analyzed batch")
            commit_analyzed_batch_span.record_exception(e)
            commit_analyzed_batch_span.set_status(
                StatusCode.ERROR, "Failed to send processed item"
            )

async def make_transaction(request):
    global TASKS
    logging.info("NEW TRANSACTION REQUEST")
    items = await request.json()
    task = asyncio.create_task(create_task(items, request.app))
    task.add_done_callback(log_callback)
    logging.info("TRANSACTION TASK CREATED")
    TASKS.append(task)
    return web.Response(text='received')

async def healthcheck(request):
    return web.Response(status=200)

app.router.add_post('/commit', make_transaction)
app.router.add_get('/', healthcheck)

async def start_background_tasks(app):
    app['monitor_task'] = asyncio.create_task(monitor_tasks(app))

async def do_claim_master(app):
    tracer = trace.get_tracer(__name__)
    await asyncio.sleep(3)
    with tracer.start_as_current_span("claim_master") as claim_master_span:
        for i in range(0, 5):
            try:
                await claim_master(
                    app['main_address'], 
                    app['web3_configuration'], 
                    app['live_configuration']
                )
                claim_master_span.set_status(StatusCode.OK)
                logging.info("CLAIM MASTER OK")
                break
            except ValueError as ve:
                if "balance is too low" in ve.args[0].get("message", ""):
                    for i in range(0, 3):
                        try:
                            await faucet(app['web3_configuration'])
                            break
                        except:
                            timeout = i * 1.5 + 1
                            logging.exception(
                                f"An error occured during faucet (attempt {i}) (retry in {timeout})"
                            )
                            await asyncio.sleep(timeout)
            except Exception as e:
                logging.exception(
                    "An error occured while claiming master"
                )
                claim_master_span.record_exception(e)
                claim_master_span.set_status(
                    StatusCode.ERROR, "Failed to Claim Master"
                )


def start_transactioneer():
    if os.getenv('TRACING'):
        setup_tracing()
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    port = int(os.environ.get("PORT", "8000"))
    main_address = os.environ["main_address"]
    logging.info(
        f"Hello World! I'm TRANSACTIONEER running on {port} with {main_address}"
    )
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)

    logging.info(f"Starting server on {port}")
    app.on_startup.append(configuration_init)
    app.on_startup.append(start_background_tasks)
    app.on_startup.append(do_claim_master)
    app.on_startup.append(get_leaderboard)
    app['main_address'] = main_address

    try:
        asyncio.run(web._run_app(app, port=port, handle_signals=True))
    except KeyboardInterrupt:
        os._exit(0)

if __name__ == '__main__':
    start_transactioneer()
