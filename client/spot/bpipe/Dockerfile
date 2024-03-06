FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04 as with_python

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


# Ensure pip is up-to-date for the compiled Python 3.10
RUN python3.10 -m ensurepip
RUN python3.10 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# set display port to avoid crash
ENV DISPLAY=:99

RUN rm -rf /tmp

FROM with_python as with_deps

RUN pip3.10 install opentelemetry-api \
        opentelemetry-sdk \
        opentelemetry-exporter-jaeger \
        opentelemetry-instrumentation-aiohttp-client \
        opentelemetry-sdk opentelemetry-exporter-otlp \
        aioprometheus==23.3.0

RUN pip3.10 install --no-cache-dir \
        'git+https://github.com/exorde-labs/exorde_data.git@full' \
        asyncio \
        aiohttp \
        pyyaml \
        tiktoken==0.4.0 \
        numpy==1.23.4 \
        fasttext==0.9.2 \
        fasttext-langdetect==1.0.5 \
        huggingface_hub==0.14.1 \
        pandas==1.5.3 \
        sentence-transformers==2.2.2 \
        tensorflow==2.12.0 \
        torch==1.13.0 \
        argostranslate==1.8.0 \
        wtpsplit==1.3.0 \
        finvader==1.0.2 \
        vaderSentiment==3.3.2 \
        swifter==1.3.4

# Clean cache now that we have installed everything
RUN rm -rf /root/.cache/* \
    && rm -rf /root/.local/cache/*

FROM with_deps as with_models

COPY ./install.py /app/install.py
RUN python3.10 /app/install.py

FROM with_models as with_code

WORKDIR /app
COPY ./src/* /app/.


ENTRYPOINT ["python3.10", "/app/bpipe.py"]
