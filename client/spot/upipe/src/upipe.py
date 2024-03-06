#! python3.10

from wtpsplit import WtP # wtpsplit/issues/10

import logging, os, signal, time, random

import asyncio
from aioprometheus.collectors import REGISTRY
from aioprometheus.renderer import render
from aiohttp import web, ClientSession

from concurrent.futures import ThreadPoolExecutor
import threading

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.status import Status
from opentelemetry.trace import StatusCode
from aioprometheus.collectors import Counter, Histogram, Gauge

from exorde_data import Item
from process import process, TooBigError
from exorde_data.get_live_configuration import get_live_configuration, LiveConfiguration


from lab_initialization import lab_initialization
# from split_item import split_item # UNUSED TODO


def setup_tracing():
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "item_processor"
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


queue_length_gauge = Gauge(
    "process_queue_length", 
    "Current number of items in the processing queue"
)
receive_counter = Counter(
    "processor_reception", 
    "Number of 'receive' calls by item processor"
)
internal_loop_count = Counter(
    "processor_cycle",
    "Amount of cycle the processor thread has ran"
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
    return web.Response(text="Hello world", status=200)

async def metrics(request):
    content, http_headers = render(REGISTRY, [request.headers.get("accept")])
    return web.Response(body=content, headers=http_headers)

class Busy(Exception):
    """Thread Queue is busy handeling another item"""

    def __init__(self, message="Thread queue is busy handeling another item"""):
        self.message = message
        super().__init__(self.message)


from exorde_data import CreatedAt, Content, Domain, Url, Title

# Summary, Picture, Author, ExternalId, ExternalParentId,

async def processing_logic(app, current_item):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("process_item") as processing_span:
        try:
            logging.info("PROCESS START")
            processed_item = process(
                current_item, app["lab_configuration"], 
                app["live_configuration"]["max_depth"]
            )
            logging.info(f"PROCESS OK - ADDING TO BATCH : {processed_item}")
            processing_span.set_status(StatusCode.OK)

            # New span for sending the processed item
            with tracer.start_as_current_span("send_processed_item") as send_span:
                target = random.choice(os.getenv('batch_target', '').split(','))
                if target:
                    async with ClientSession() as session:
                        async with session.post(
                            target, json=processed_item
                        ) as response:
                            if response.status == 200:
                                successful_process.inc({})
                                logging.info("PROCESSED ITEM SENT SUCCESSFULLY")
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
            logging.error("Processing timed out")
            processing_span.set_status(
                Status(StatusCode.ERROR, "Processing timed out")
            )
        except TooBigError as e:
            too_big_counter.inc({})
            processing_span.set_status(
                Status(StatusCode.ERROR, str(e))
            )
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            processing_span.set_status(
                Status(StatusCode.ERROR, "Unexpected error during processing")
            )
            processing_span.record_exception(e)

def thread_function(app):
    """
    Thread function that processes items. This function runs in a separate thread.
    """
    logging.info("Running thread function")
    executor = ThreadPoolExecutor()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def process_internal():
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
                if current_item is not None:
                    logging.info("processing new item")
                    await asyncio.wait_for(
                        processing_logic(app, current_item), timeout=1
                    )
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
            item: Item = Item(
                created_at=CreatedAt(raw_item['created_at']),
                title=Title(raw_item.get('title', '')),
                content=Content(raw_item['content']),
                domain=Domain(raw_item['domain']),
                url=Url(raw_item['url'])
            )
            await app['process_queue'].put(item)
            queue_length_gauge.set({}, app['process_queue'].qsize())
            receive_counter.inc({})
            logging.info(item)
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
    lab_configuration = lab_initialization()
    app['live_configuration'] = live_configuration
    app['lab_configuration'] = lab_configuration


def start_spotter():
    setup_tracing()
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    port = int(os.environ.get("PORT", "8000"))
    logging.info(f"Hello World! I'm running on {port}")
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
