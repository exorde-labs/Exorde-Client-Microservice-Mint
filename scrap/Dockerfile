FROM python:3.10.11 as base

# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean

# Install pandas using pip
RUN pip install pandas

# Use a single RUN command to minimize the number of layers
RUN apt-get update -y && \
    apt-get upgrade -y --fix-missing && \
    apt-get install -y --fix-missing chromium chromium-driver xvfb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver

RUN pip3.10 install aioprometheus==23.3.0

RUN pip3.10 install opentelemetry-api \
        opentelemetry-sdk \
        opentelemetry-exporter-jaeger \
        opentelemetry-instrumentation-aiohttp-client \
        opentelemetry-sdk opentelemetry-exporter-otlp

RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/exorde_data"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/ap98j3envoubi3fco1kc"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/ch4875eda56be56000ac"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/masto65ezfd86424f69a"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/rss007d0675444aa13fc"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/youtube00e1f862e5eff"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/hackbc9419ab11eebe56"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/tradview251ae30a11ee"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/bitcointalk4de40ec26"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/hackbc9419ab11eebe56"

FROM base as with_weibo

COPY scrap/wei223be19ab11e891bo /wei223be19ab11e891bo
RUN pip3.10 install --no-cache-dir --upgrade /wei223be19ab11e891bo

COPY scrap/a7df32de3a60dfdb7a0b /a7df32de3a60dfdb7a0b
RUN pip3.10 install --no-cache-dir --upgrade /a7df32de3a60dfdb7a0b

COPY scrap/forocoches86019fc2d4 /forocoches86019fc2d4
RUN pip3.10 install --no-cache-dir --upgrade /forocoches86019fc2d4

COPY scrap/followinc645fc950d7f /followinc645fc950d7f
RUN pip3.10 install --no-cache-dir --upgrade /followinc645fc950d7f

COPY scrap/jvc8439846094ced03ff /jvc8439846094ced03ff
RUN pip3.10 install --no-cache-dir --upgrade /jvc8439846094ced03ff

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

FROM with_weibo as exorde_scrap

COPY scrap/src /app 