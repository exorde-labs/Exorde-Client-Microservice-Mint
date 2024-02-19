FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04 as base

# Avoid interactive prompts
ENV DEBIAN_FRONTEND noninteractive

# Preconfigure selected timezone
RUN echo 'tzdata tzdata/Areas select Europe' | debconf-set-selections \
    && echo 'tzdata tzdata/Zones/Europe select Berlin' | debconf-set-selections


# Install dependencies required for compiling Python
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libffi-dev \
    libgdbm-dev \
    libc6-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev \
    git

# Download and compile Python 3.10
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz && \
    tar -xzf Python-3.10.4.tgz && \
    cd Python-3.10.4 && \
    ./configure --enable-optimizations && \
    make -j 8 && \
    make altinstall

FROM base as exorde_spotting_aa

# Ensure pip is up-to-date for the compiled Python 3.10
RUN python3.10 -m ensurepip
RUN python3.10 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install pybind11 and other Python dependencies
RUN python3.10 -m pip install --no-cache-dir pybind11

RUN pip3.10 install --no-cache-dir --upgrade 'git+https://github.com/JustAnotherArchivist/snscrape.git'
RUN pip3.10 install --no-cache-dir \
        'git+https://github.com/exorde-labs/exorde_data.git' \
        selenium==4.2.0 \
        wtpsplit==1.2.3 \
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
        finvader==1.0.2 \
        aiofiles==23.2.1 \
        keybert==0.7.0 \
        nltk==3.6.2 \
        safetensors==0.3.1 \
        numpy==1.23.4 \
        tiktoken==0.4.0 \
        feedparser==6.0.8 \
        python_dateutil==2.8.2 \
        newspaper3k==0.2.8 \
        fasttext==0.9.2 \
        fasttext-langdetect==1.0.5 \
        huggingface_hub==0.14.1 \
        pandas==1.5.3 \
        sentence-transformers==2.2.2 \
        spacy==3.5.1 \
        swifter==1.3.4 \
        tensorflow==2.12.0 \
        torch==1.13.0 \
        vaderSentiment==3.3.2 \
        yake==0.4.8 \
        argostranslate==1.8.0

FROM exorde_spotting_aa as exorde_spotting_a

RUN pip3.10 install skops \
        wtpsplit==1.2.3 


FROM exorde_spotting_a as exorde_spotting_b

# set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /app
## INSTALL ALL MODELS
COPY spot/src/lab_initialization.py /app/lab_initialization.py
COPY spot/src/protocol-configuration.yaml /app/protocol-configuration.yaml
COPY spot/src/instanciate_w3.py /app/instanciate_w3.py
COPY spot/src/pre_install.py /app/pre_install.py
COPY spot/src/get_contracts.py /app/get_contracts.py
COPY spot/src/write_web3.py /app/write_web3.py
COPY spot/src/read_web3.py /app/read_web3.py
COPY spot/src/get_static_configuration.py /app/get_static_configuration.py
COPY spot/src/get_live_configuration.py /app/get_live_configuration.py
COPY spot/src/get_worker_account.py /app/get_worker_account.py
COPY spot/src/get_protocol_configuration.py /app/get_protocol_configuration.py
COPY spot/src/get_contracts_and_abi_cnf.py /app/get_contracts_and_abi_cnf.py
COPY spot/src/get_network_configuration.py /app/get_network_configuration.py

RUN python3.10 -m spacy download en_core_web_trf

RUN python3.10 pre_install.py

RUN pip3.10 install opentelemetry-api \
        opentelemetry-sdk \
        opentelemetry-exporter-jaeger \
        opentelemetry-instrumentation-aiohttp-client \
        opentelemetry-sdk opentelemetry-exporter-otlp


FROM exorde_spotting_b as exorde_spotting

## INSTALL THE APP
RUN rm -rf spot/src
COPY spot/src/* /app

ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
ENV TRANSFORMERS_OFFLINE=1