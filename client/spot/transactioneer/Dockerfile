FROM python:3.10.11 as base

# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3.10 install --no-cache-dir aioprometheus==23.3.0 \
        madtypes \
        eth-account \
        asyncio \
        aiohttp \
        lxml \
        pyyaml \
        web3 

RUN pip3.10 install opentelemetry-api \
        opentelemetry-sdk \
        opentelemetry-exporter-jaeger \
        opentelemetry-instrumentation-aiohttp-client \
        opentelemetry-sdk opentelemetry-exporter-otlp

FROM base as transactioneer

WORKDIR /app

RUN pip3.10 install --no-cache-dir \
        'git+https://github.com/exorde-labs/exorde_data.git@full'

## INSTALL THE APP
COPY ./src/* /app
ENTRYPOINT ["python3.10", "/app/transactioneer.py"]
