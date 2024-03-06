# Exorde Spotting


## Components overview

| container | image | has models | Image size | description | GPU Support |
| --- | --- | --- | --- | --- | --- |
| transactioneer | transactioneer | no | 1.25 G | Web3 interaction | not required |
| bpipe | bpipe | yes | 14.6 G | Batch processing | yes (recomended) |
| upipe | upipe | yes | 19.7 G | Unit processing | yes (not recomended) |

## How to run

- `MAIN_ADDRESS` is specified as an ENV variable

```bash
MAIN_ADDRESS=... docker compose up -d
```
## GPU Support

The bpipe can have GPU support enabled using

```
... docker compose -f docker-compose.yaml -f enable-gpu.yaml up -d
```

The `bpipe` stands for `batch_data_pipe` and GPU support is recommended on it.


## Horizontal Scaling

GPU support is not recommended on `upipe` as the loading time exceeds the benefits. 
For this component horizontal scaling is prefered using `UPIPE_SIZE`

```
... UPIPE_SIZE=2 docker-compose up
```

## Example

Spawning the client with 5 upipe and GPU support :
```
MAIN_ADDRESS=... UPIPE_SIZE=5 docker-compose -f docker-compose.yaml -f enable-gpu.yaml up -d
```

## Monitoring

## About it
> scrap -> upipe -> bpipe -> transactioneer
