FROM python:3.10.11 as base


# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip3.10 install --no-cache-dir \
        'git+https://github.com/exorde-labs/exorde_data.git' \
        aioprometheus==23.3.0 \
        madtypes \
        eth-account \
        asyncio \
        aiohttp \
        lxml \
        HTMLParser \
        pytz \
        pyyaml \
        web3 \
        packaging \
        aiofiles==23.2.1 \
        nltk==3.6.2 \
        numpy==1.23.4 \
        tiktoken==0.4.0 \
        feedparser==6.0.8 \
        python_dateutil==2.8.2

# set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /app

FROM exorde_spotting_b as exorde_spotting

## INSTALL THE APP
COPY spot/src/* /app

RUN pip3.10 install opentelemetry-api \
        opentelemetry-sdk \
        opentelemetry-exporter-jaeger \
        opentelemetry-instrumentation-aiohttp-client \
        opentelemetry-sdk opentelemetry-exporter-otlp

ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python