# Exorde Spotting

## 🐳 Spotting Stack Overview

- [all repositories on this subject](https://github.com/search?q=topic%3Aexorde-spot+org%3Aexorde-labs+&type=repositories)

### Minimal required images

#### Data Processing

| image | has models | Image size | description | GPU Support | Build Status | Version |
| --- | --- | --- | --- | --- | --- | --- |
| [transactioneer](https://github.com/exorde-labs/transactioneer/tree/main) | no |  ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/transactioneer) | Web3 interaction | not required | [![Build](https://github.com/exorde-labs/transactioneer/actions/workflows/build_docker_production.yaml/badge.svg)](https://github.com/exorde-labs/transactioneer/actions/workflows/build_docker_production.yaml) | ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/transactioneer)|
| [bpipe](https://github.com/exorde-labs/bpipe/tree/main) | yes |  ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/bpipe) | Batch processing | yes (recomended) | [![Build](https://github.com/exorde-labs/bpipe/actions/workflows/build_docker_production.yaml/badge.svg)](https://github.com/exorde-labs/bpipe/actions/workflows/build_docker_production.yaml) | ![Docker Image Version](https://img.shields.io/docker/v/exordelabs/bpipe)|
| [upipe](https://github.com/exorde-labs/upipe/tree/main) | yes |  ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/upipe) | Unit processing | yes (not recomended) | [![Build](https://github.com/exorde-labs/upipe/actions/workflows/build_docker_production.yaml/badge.svg)](https://github.com/exorde-labs/upipe/actions/workflows/build_docker_production.yaml) |![Docker Image Version](https://img.shields.io/docker/v/exordelabs/upipe)|
| [container_scout](https://github.com/exorde-labs/container_scout/tree/main) | no | ![Docker Image Size](https://img.shields.io/docker/image-size/exordelabs/container_scout)| Orchestration & Monitoring | not required | [![Build](https://github.com/exorde-labs/container_scout/actions/workflows/build_docker_production.yaml/badge.svg)](https://github.com/exorde-labs/container_scout/actions/workflows/build_docker_production.yaml) |![Docker Image Version](https://img.shields.io/docker/v/exordelabs/container_scout)|


#### Data Retrieval

- [Every available `spot` driver](https://github.com/search?q=topic%3Aexorde-spot-driver+org%3Aexorde-labs+&type=repositories)


#### 👁️ Monitoring
