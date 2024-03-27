




> - [Every repository on this subject](https://github.com/search?q=topic%3Aexorde-spot+org%3Aexorde-labs+&type=repositories)

## TLDR

```
MAIN_ADDRESS=... SPOTTERS_AMOUNT=2 docker compose up -d
```

# 📘 How to mine EXD

The client is ran using two `docker compose` files.
- `docker-compose.yaml` : processing and web3
- `spotters.yaml` : scraping services

## 1️⃣ Core
| image | Image size | description | Version | Pulls |
| --- |  --- | --- | --- | --- |
| [transactioneer](https://github.com/exorde-labs/transactioneer/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/transactioneer) | Web3 interaction | ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/transactioneer)| ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/transactioneer) |
| [bpipe](https://github.com/exorde-labs/bpipe/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/bpipe) | Batch processing |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/bpipe)| ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/bpipe ) |
| [upipe](https://github.com/exorde-labs/upipe/tree/main) |  ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/upipe) | Unit processing | ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/upipe)| ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/upipe) |
| [orchestrator](https://github.com/exorde-labs/orchestrator/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/orchestrator)| Orchestration & Monitoring | ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/orchestrator)| ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/orchestrator) |


### Available parameters
- `MAIN_ADDRESS` is specified as an ENV variable
- `UPIPE_SIZE`: allow to spawn multiple `upipe` service, which are responsible for CPU unit-processing
- `UPIPE_PROCESSING_TIMEOUT`: allows you to specify the timeout on CPU processing logic, a short time can be used on better machine while slower machine will fall in the 8s range.
- `TRACE`: enable tracing

### Example
```bash
MAIN_ADDRESS=... docker compose up -d
```
## :two: [Spotters](https://github.com/exorde-labs/spot/tree/main)
> - [Every available `spot` driver repositories](https://github.com/search?q=topic%3Aexorde-spot-driver+org%3Aexorde-labs+&type=repositories)

| image | Image size | Version | Pulls |
| --- |  --- | --- | --- |
| [spotseekingalphad89ba32s](https://github.com/exorde-labs/seekingalphad89ba32s/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotseekingalphad89ba32s) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotseekingalphad89ba32s) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotseekingalphad89ba32s) | 
| [spotbitcointalk4de40ec26](https://github.com/exorde-labs/bitcointalk4de40ec26/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotbitcointalk4de40ec26) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotbitcointalk4de40ec26) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotbitcointalk4de40ec26) | 
| [spotjvc8439846094ced03ff](https://github.com/exorde-labs/jvc8439846094ced03ff/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotjvc8439846094ced03ff) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotjvc8439846094ced03ff) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotjvc8439846094ced03ff) | 
| [spotrss007d0675444aa13fc](https://github.com/exorde-labs/rss007d0675444aa13fc/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotrss007d0675444aa13fc) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotrss007d0675444aa13fc) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotrss007d0675444aa13fc) | 
| [spotch4875eda56be56000ac](https://github.com/exorde-labs/ch4875eda56be56000ac/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotch4875eda56be56000ac) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotch4875eda56be56000ac) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotch4875eda56be56000ac) | 
| [spotforocoches86019fc2d4](https://github.com/exorde-labs/forocoches86019fc2d4/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotforocoches86019fc2d4) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotforocoches86019fc2d4) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotforocoches86019fc2d4) | 
| [spothackbc9419ab11eebe56](https://github.com/exorde-labs/hackbc9419ab11eebe56/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spothackbc9419ab11eebe56) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spothackbc9419ab11eebe56) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spothackbc9419ab11eebe56) | 
| [spotmasto65ezfd86424f69a](https://github.com/exorde-labs/masto65ezfd86424f69a/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotmasto65ezfd86424f69a) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotmasto65ezfd86424f69a) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotmasto65ezfd86424f69a) | 
| [spotnostr5fa856e7234fbee](https://github.com/exorde-labs/nostr5fa856e7234fbee/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotnostr5fa856e7234fbee) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotnostr5fa856e7234fbee) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotnostr5fa856e7234fbee) | 
| [spota7df32de3a60dfdb7a0b](https://github.com/exorde-labs/a7df32de3a60dfdb7a0b/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spota7df32de3a60dfdb7a0b) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spota7df32de3a60dfdb7a0b) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spota7df32de3a60dfdb7a0b) | 
| [spotap98j3envoubi3fco1kc](https://github.com/exorde-labs/ap98j3envoubi3fco1kc/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotap98j3envoubi3fco1kc) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotap98j3envoubi3fco1kc) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotap98j3envoubi3fco1kc) | 
| [spotlemmyw04b6eb792ca4a1](https://github.com/exorde-labs/lemmyw04b6eb792ca4a1/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotlemmyw04b6eb792ca4a1) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotlemmyw04b6eb792ca4a1) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotlemmyw04b6eb792ca4a1) | 
| [spotwei223be19ab11e891bo](https://github.com/exorde-labs/wei223be19ab11e891bo/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotwei223be19ab11e891bo) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotwei223be19ab11e891bo) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotwei223be19ab11e891bo) | 
| [spotfollowinc645fc950d7f](https://github.com/exorde-labs/followinc645fc950d7f/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotfollowinc645fc950d7f) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotfollowinc645fc950d7f) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotfollowinc645fc950d7f) | 
| [spotyoutube00e1f862e5eff](https://github.com/exorde-labs/youtube00e1f862e5eff/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spotyoutube00e1f862e5eff) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spotyoutube00e1f862e5eff) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spotyoutube00e1f862e5eff) | 
| [spottradview251ae30a11ee](https://github.com/exorde-labs/tradview251ae30a11ee/tree/main) | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/spottradview251ae30a11ee) |  ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/spottradview251ae30a11ee) | ![Docker Pulls](https://img.shields.io/docker/pulls/exordelabs/spottradview251ae30a11ee) | 

### Custom `spotters` distribution
> note that this is only for customization and you do not require this if you are using `SPOTTERS_AMOUNT` which will spawn `spotters` for you.

[`spotters.yaml`](./docker-compose.yaml)  provides an easy way to launch the different spotters with different redundancy parameters, each module is parametrable with it's three first leters (jumping over `spot`)

```shell
rss=1 bit=1 jvc=1 ch4=1 for=1 hac=1 mas=1 nos=1 a7d=1 ap9=1 lem=1 wei=1 fol=1 you=1 tra=1 docker compose -f spotters.yaml up -d
```

The `spotters.yaml` is connected with processing services in `docker-compose` trough a docker network called `exorde-network`. You do not need launching them together. 
