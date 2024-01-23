FROM python:3.10.11 as base


# Update and install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y chromium chromium-driver xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/chromedriver  /usr/local/bin/chromedriver


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

FROM base as exorde_spotting_a

RUN pip3.10 install skops \
        wtpsplit==1.2.3 


FROM exorde_spotting_a as exorde_spotting_b

# set display port to avoid crash
ENV DISPLAY=:99

## INSTALL ALL MODELS
COPY spot/install/pre_install.py /app/exorde_install_models.py
WORKDIR /app
RUN python3.10 exorde_install_models.py \
    && rm -rf /root/.cache/* \
    && rm -rf /root/.local/cache/*
RUN python3.10 -m spacy download en_core_web_trf \
    && rm -rf /root/.cache/*

FROM exorde_spotting_b as exorde_spotting

## INSTALL THE APP
COPY spot/src/* /app

## ENTRY POINT IS MAIN.PY
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
