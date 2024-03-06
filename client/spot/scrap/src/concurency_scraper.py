#! python3.10
from aioprometheus.collectors import REGISTRY
from aioprometheus.renderer import render
from aiohttp import web, ClientSession
import logging
import asyncio
import os
from importlib import import_module
import signal
from aioprometheus.collectors import Counter

from scraper_configuration import get_scrapers_configuration
from keywords import choose_keyword

TASKS = {}
TASK_COMPLETED = None
SHUTDOWN = False

app = web.Application()

module_list = [
    "ap98j3envoubi3fco1kc",
    "ch4875eda56be56000ac",
    "masto65ezfd86424f69a",
    "rss007d0675444aa13fc",
    "youtube00e1f862e5eff",
    "wei223be19ab11e891bo",
    "hackbc9419ab11eebe56",
    "tradview251ae30a11ee",
    "bitcointalk4de40ec26",
    "hackbc9419ab11eebe56",
    "jvc8439846094ced03ff"
]

push_counter = Counter("push", "Number of data pushed to spotting blades")


def get_scraper_concurency_configuration() -> dict[str, int]:
    scraper_configuration = {}
    for module in module_list:
        scraper_configuration[module] = int(os.environ.get(module, 0))
    return scraper_configuration

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.status import Status
from opentelemetry.trace import StatusCode
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider


async def push_item(url, item):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("push_item") as push_item_span:
        async with ClientSession() as session:
            try:
                logging.info('Pushing item')
                await session.post(url, json=item)
                push_item_span.set_status(StatusCode.OK)
            except Exception as e:
                push_item_span.set_status(Status(StatusCode.ERROR, str(err)))
                logging.exception("An error occured while pushing an item")
                push_item_span.record_exception(e)

def setup_tracing():
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "scraper"
    })

    trace_provider = TracerProvider(resource=resource)
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(trace_provider)

async def worker_task(scrap_module_name):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("worker_initialization") as worker_initialization_span:
        try:
            with tracer.start_as_current_span("worker_initialization_import_module") as worker_initialization_import_module_span:
                module = import_module(scrap_module_name)
                worker_initialization_import_module_span.set_status(StatusCode.OK)

            with tracer.start_as_current_span("worker_initialization_get_scrapers_configuration") as worker_initialization_get_scrapers_configuration_span:
                scraper_configuration = await get_scrapers_configuration()
                worker_initialization_get_scrapers_configuration_span.set_status(StatusCode.OK)

            choosen_module_path = f"https://github.com/exorde-labs/{scrap_module_name}"
            generic_modules_parameters = scraper_configuration.generic_modules_parameters
            specific_parameters = scraper_configuration.specific_modules_parameters.get(
                choosen_module_path, {}
            )
            

            with tracer.start_as_current_span("worker_initialization_choose_keyword") as choose_keyword_span:
                keyword = await choose_keyword(
                    choosen_module_path, scraper_configuration
                )
                choose_keyword_span.set_status(StatusCode.OK)
            
            parameters = {
                "url_parameters": {"keyword": keyword},
                "keyword": keyword,
            }
            parameters.update(generic_modules_parameters)
            parameters.update(specific_parameters)

            with tracer.start_as_current_span("worker_get_iterator") as get_iterator_span:
                iterator = module.query(parameters).__aiter__()
                get_iterator_span.set_status(StatusCode.OK)
            worker_initialization_span.set_status(StatusCode.OK)
        except Exception as e:
            worker_initialization_span.record_exception(e)
            worker_initialization_span.set_status(StatusCode.ERROR, "Failed to init scrap worker")


    try:
        logging.info(f"Working on: {scrap_module_name} : {iterator}")
        while True:
            await asyncio.sleep(5)
            item = await asyncio.wait_for(iterator.__anext__(), timeout=120)
            if item:
                await push_item(os.getenv('spotting_target'), item)
                push_counter.inc({"module": module.__name__})
    except Exception as e:
        logging.exception(f"Done with: {scrap_module_name} : {iterator}")
    finally:
        if TASK_COMPLETED:
            TASK_COMPLETED(scrap_module_name)


def ensure_tasks(scrap_module_name, config):
    global TASKS
    if scrap_module_name not in TASKS:
        TASKS[scrap_module_name] = []
    tasks = TASKS[scrap_module_name]
    tasks = [t for t in tasks if not t.done()]
    TASKS[scrap_module_name] = tasks
    for _ in range(config[scrap_module_name] - len(tasks)):
        new_task = asyncio.create_task(worker_task(scrap_module_name))
        tasks.append(new_task)


async def background_task():
    global TASKS, TASK_COMPLETED, SHUTDOWN
    config = get_scraper_concurency_configuration()
    TASKS = {scrap_module_name: [] for scrap_module_name in config}
    TASK_COMPLETED = lambda scrap_module_name: ensure_tasks(scrap_module_name, config)

    while not SHUTDOWN:
        for scrap_module_name, required_count in config.items():
            ensure_tasks(scrap_module_name, config)
        await asyncio.sleep(1)

async def start_background_task(app):
    global SHUTDOWN
    SHUTDOWN = False
    asyncio.create_task(background_task())

async def cleanup_background_task(app):
    logging.info("Cleanup background task")
    os._exit(0)

app.on_startup.append(start_background_task)
app.on_cleanup.append(cleanup_background_task)

def terminate(signal, frame):
    os._exit(0)

async def metrics(request):
    content, http_headers = render(REGISTRY, [request.headers.get("accept")])
    return web.Response(body=content, headers=http_headers)

async def hello(request):
    return web.Response(text="Hello, World!")

app.router.add_get("/", hello)
app.router.add_get("/metrics", metrics)

def start_scraper():
    setup_tracing()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    port = int(os.environ.get("PORT", "8080"))
    logging.info(f"Hello World! I'm running on {port}")
    logging.info("Scraping configuration:")
    scraper_configuration = get_scraper_concurency_configuration()
    for module in scraper_configuration:
        logging.info(f"\t{module} = {scraper_configuration[module]}")
    logging.info(f"Will push data to: {os.environ.get('spotting_target')}")

    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)

    logging.info(f"Starting server on {port}")
    try:
        asyncio.run(web._run_app(app, port=port, handle_signals=True))
    except KeyboardInterrupt:
        os._exit(0)

if __name__ == '__main__':
    start_scraper()