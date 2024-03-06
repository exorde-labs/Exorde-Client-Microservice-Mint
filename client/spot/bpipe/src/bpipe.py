#! python3.10

import logging, os

import asyncio
import signal
from aioprometheus.collectors import REGISTRY
from aioprometheus.renderer import render
from aiohttp import web, ClientSession
import time

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.status import Status
from opentelemetry.trace import StatusCode

import threading


from exorde_data import (
    CreatedAt, 
    Content, 
    Domain, 
    Url, 
    Title, 
    Classification, 
    Translation, 
    Processed, 
    Language, 
    Translated, 
    Keywords

)

from process_batch import process_batch

def setup_tracing():
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "batch_processor"
    })

    trace_provider = TracerProvider(resource=resource)
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(trace_provider)
    
app = web.Application()

from aioprometheus.collectors import Counter, Histogram, Gauge

receive_counter = Counter(
    "batch_processor_reception", 
    "Number of 'receive' calls by item processor"
)
internal_loop_count = Counter(
    "batch_processor_cycle",
    "Amount of cycle the processor thread has ran"
)
too_big_counter = Counter(
    "batch_processor_too_big", 
    "Number of items that are marked as too big by processor"
)
process_histogram = Histogram(
    "batch_process_execution_duration_seconds", 
    "Duration of 'process' in seconds", 
    buckets=[0, 1, 2, 3, 4, 5, 10, 15, 20]
)
successful_process = Counter(
    "batch_process_successful", 
    "Amount of successfully processed items"
)
process_error = Counter(
    "batch_process_error", 
    "Amount of errored process"
)
batch_size_gauge = Gauge(
    "batch_size", 
    "Current batch size"
)

def terminate(signal, frame):
    os._exit(0)

async def healthcheck(__request__):
    return web.Response(text="Hello world", status=200)

async def metrics(request):
    content, http_headers = render(REGISTRY, [request.headers.get("accept")])
    return web.Response(body=content, headers=http_headers)

from exorde_data import Item

from exorde_data.get_live_configuration import get_live_configuration, LiveConfiguration

from concurrent.futures import ThreadPoolExecutor

class Busy(Exception):
    """Thread Queue is busy handeling another item"""

    def __init__(self, message="Thread queue is busy handeling another item"""):
        self.message = message
        super().__init__(self.message)


from exorde_data import CreatedAt, Content, Domain, Url, Title

# Summary, Picture, Author, ExternalId, ExternalParentId,

async def processing_logic(app, batch):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("process_batch") as processing_span:
        try:
            timeout = 60
            logging.info("PROCESS START")
            processed_batch = process_batch(batch, app["static_configuration"])
            logging.info(f"PROCESS OK - ADDING TO BATCH : {processed_batch}")
            processing_span.set_status(StatusCode.OK)
            
            # New span for sending the processed batch
            with tracer.start_as_current_span("send_processed_batch") as send_span:
                target = os.getenv('transactioneer')
                if target:
                    async with ClientSession() as session:
                        async with session.post(
                            f"{target}/commit", json=processed_batch['items']
                        ) as response:
                            if response.status == 200:
                                successful_process.inc({})
                                logging.info(
                                    "PROCESSED BATCH SENT SUCCESSFULLY"
                                )
                                send_span.set_status(StatusCode.OK)
                            else:
                                logging.error(
                                    f"Failed to send processed item, status code: {response.status}"
                                )
                                send_span.set_status(
                                    StatusCode.ERROR, "Failed to send processed item"
                                )
                else:
                    logging.info("No batch_target configured")
                    send_span.set_status(
                        Status(StatusCode.ERROR, "No target configured")
                    )

        except asyncio.TimeoutError:
            logging.error("Batch Processing timed out")
            processing_span.set_status(
                Status(StatusCode.ERROR, "Processing timed out")
            )
        except TooBigError as e:
            too_big_counter.inc({})
            processing_span.set_status(Status(StatusCode.ERROR, str(e)))
        except Exception as e:
            logging.exception(f"Unexpected error: {e}")
            processing_span.set_status(
                Status(StatusCode.ERROR, "Unexpected error during processing")
            )
            processing_span.record_exception(e)

max_batch_size = os.getenv("batch_size", 20)
def batch_reached_mature_size(batch) -> bool:
    global max_batch_size
    logging.info(f"BATCH SIZE IS {len(batch)} / {max_batch_size} ")
    batch_size_gauge.set({}, len(batch))
    if len(batch) >= int(max_batch_size):
        return True
    return False

def thread_function(app):
    """
    Thread function that processes items. This function runs in a separate thread.
    """
    logging.info("Running thread function")
    executor = ThreadPoolExecutor()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    

    async def process_internal():
        batch = []
        logging.info("Running internal")
        tracer = trace.get_tracer(__name__)
        while True:
            logging.info("internal loop")
            try:
                internal_loop_count.inc({})
                try:
                    current_item = await asyncio.wait_for(
                        app['process_queue'].get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    current_item = None
                if current_item != None:
                    batch.append(current_item)
                    if batch_reached_mature_size(batch):
                        batch_copy = [
                            (i + 1, item) for i, item in enumerate(batch.copy())
                        ]
                        logging.info("MAKING A COPY")
                        logging.info(batch_copy)
                        batch = []
                        logging.info("processing new batch")
                        await processing_logic(app, batch_copy)
            except:
                logging.exception("An error occured in processor thread")
        await asyncio.sleep(1)

    loop.run_until_complete(process_internal())

def start_processing_thread(app):
    """
    Starts the processing thread and monitors it for restart if it dies.
    """
    stop_event = threading.Event()

    def monitor_thread():
        while not stop_event.is_set():
            thread = threading.Thread(target=thread_function, args=(app, ))
            thread.start()
            thread.join()
            if not stop_event.is_set():
                logging.warning("Processing thread died. Restarting...")
    
    monitor = threading.Thread(target=monitor_thread)
    monitor.start()
    return stop_event, monitor


async def setup_thread(app):
    app['process_queue'] = asyncio.Queue()
    stop_event, monitor_thread = start_processing_thread(app)
    app['stop_event'] = stop_event
    app['monitor_thread'] = monitor_thread

# Make sure to properly handle cleanup on app shutdown
async def cleanup(app):
    app['stop_event'].set()  # Signal the thread to stop
    app['monitor_thread'].join()  # Wait for the monitor thread to finish


async def receive_item(request):
    global receive_counter
    logging.info("receiving new item")
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("receive_item") as span:
        start_time = time.time()  # Record the start time

        raw_item = await request.json()
        try:
            processed_item: Processed = Processed(
                classification=Classification(
                    label=raw_item["classification"]['label'], 
                    score=raw_item['classification']['score']
                ),
                translation=Translation(
                    language=Language(raw_item['translation']['language']), 
                    translation=Translated(raw_item['translation']['translation'])
                ),
                top_keywords=Keywords(list(raw_item['top_keywords'])),
                item=Item(
                    created_at=CreatedAt(raw_item['item']['created_at']),
                    title=Title(raw_item['item'].get('title', '')),
                    content=Content(raw_item['item']['content']),
                    domain=Domain(raw_item['item']['domain']),
                    url=Url(raw_item['item']['url'])
                )
            )
            await app['process_queue'].put(processed_item)
            receive_counter.inc({})
            logging.info(processed_item)
            span.set_status(StatusCode.OK)
            logging.info("Item added to queue")
        except Exception as e:
            logging.exception("An error occurred asserting an item structure")
            span.record_exception(e)
            span.set_status(StatusCode.ERROR, "Error processing item")

        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration

        span.set_attribute("processing_duration", duration)  # Record the duration as an attribute
        logging.info(f"Item handled in {duration} seconds")  # Log the duration

    return web.Response(text="received")

app.router.add_post('/', receive_item)
app.router.add_get('/', healthcheck)
app.router.add_get('/metrics', metrics)

async def configuration_init(app):
    # arguments, live_configuration
    live_configuration: LiveConfiguration = await get_live_configuration()
    app['live_configuration'] = live_configuration


def start_spotter():
    setup_tracing()
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    port = int(os.environ.get("PORT", "8000"))
    logging.info(f"Hello World ! I'm BATCH_PROCESSOR and running on {port}")
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)

    logging.info(f"Starting server on {port}")
    app.on_startup.append(configuration_init)
    app.on_startup.append(setup_thread)
    try:
        asyncio.run(web._run_app(app, port=port, handle_signals=True))
    except KeyboardInterrupt:
        os._exit(0)


if __name__ == '__main__':
    start_spotter()
