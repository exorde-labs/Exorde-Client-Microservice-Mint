# Exorde Spotting

## 🐳 Components overview

| image | has models | Image size | description | GPU Support | build |
| --- | --- | --- | --- | --- | --- |
| transactioneer | no | 1.25 G | Web3 interaction | not required | [![Build & Publish the container image - production](https://github.com/exorde-labs/transactioneer/actions/workflows/build_docker_production.yaml/badge.svg)](https://github.com/exorde-labs/transactioneer/actions/workflows/build_docker_production.yaml) |
| bpipe | yes | 14.6 G | Batch processing | yes (recomended) | [![Build & Publish the container image - production](https://github.com/exorde-labs/bpipe/actions/workflows/build_docker_production.yaml/badge.svg)](https://github.com/exorde-labs/bpipe/actions/workflows/build_docker_production.yaml) |
| upipe | yes | 19.7 G | Unit processing | yes (not recomended) | [![Build](https://github.com/exorde-labs/upipe/actions/workflows/build_docker_production.yaml/badge.svg)](https://github.com/exorde-labs/upipe/actions/workflows/build_docker_production.yaml) |
| *-scraper | no | 2.24 G | Scraping | No not required |  |

### 📘 How to run

- `MAIN_ADDRESS` is specified as an ENV variable

```bash
MAIN_ADDRESS=... docker compose up -d
```

### Extended parameters

To further customize the compose file, docker compose uses an extend system.

### ⚡ GPU Support (bpipe/gpu.yaml)

- `bpipe` stands for `batch_data_pipe` and GPU support is recommended for it.

```
... docker compose -f docker-compose.yaml -f ./bpipe/gpu.yaml up -d
```

> note : we do not provide horizontal scaling options for bpipe as it is dificult to configure both GPU
> and horizontal scaling ([more about this](https://github.com/exorde-labs/Exorde-Client-Microservice-Mint/issues/1))

### 🧑‍🤝‍🧑 Horizontal Scaling (upipe/hoz.yaml)

- `upipe` stands for `unit_data_pipe` and GPU support is not recommended as the loading time exceeds the benefits. 
For this component horizontal scaling is prefered using `UPIPE_SIZE`

```
... UPIPE_SIZE=2 docker-compose -f docker-compose -f ./upipe/hoz.yaml up
```

### 📘 Example

- Spawning the client with 5 upipe and GPU support :
```
MAIN_ADDRESS=... UPIPE_SIZE=5 docker-compose -f docker-compose.yaml -f ./bpipe/gpu.yaml -f ./upipe/hoz.yaml up -d
```

### 👁️ Monitoring

### 💬 About it
> scrap -> upipe -> bpipe -> transactioneer
