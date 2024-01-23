FROM python:3.10.11 as base

# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean


# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y chromium chromium-driver xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/chromedriver  /usr/local/bin/chromedriver

RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/exorde_data"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/ap98j3envoubi3fco1kc"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/ch4875eda56be56000ac"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/masto65ezfd86424f69a"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/rss007d0675444aa13fc"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/youtube00e1f862e5eff"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/wei223be19ab11e891bo"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/hackbc9419ab11eebe56"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/tradview251ae30a11ee"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/bitcointalk4de40ec26"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/hackbc9419ab11eebe56"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/jvc8439846094ced03ff"
RUN pip3.10 install --no-cache-dir --upgrade "git+https://github.com/exorde-labs/a7df32de3a60dfdb7a0b"
RUN pip3.10 install aioprometheus==23.3.0

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

FROM base as exorde_scrap

COPY scrap/src /app 
