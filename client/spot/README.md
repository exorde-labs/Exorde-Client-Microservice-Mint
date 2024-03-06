# Exorde Spotting

## Components overview

| image | has models | Image size | description | GPU Support |
| --- | --- | --- | --- | --- |
| transactioneer | no | 1.25 G | Web3 interaction | not required |
| bpipe | yes | 14.6 G | Batch processing | yes (recomended) |
| upipe | yes | 19.7 G | Unit processing | yes (not recomended) |
| *-scraper | no | 2.24 G | Scraping | No not required |

### How to run

- `MAIN_ADDRESS` is specified as an ENV variable

```bash
MAIN_ADDRESS=... docker compose up -d
```
### GPU Support

- `bpipe` stands for `batch_data_pipe` and GPU support is recommended for it.

```
... docker compose -f docker-compose.yaml -f enable-gpu.yaml up -d
```



### Horizontal Scaling

- `upipe` stands for `unit_data_pipe` and GPU support is not recommended as the loading time exceeds the benefits. 
For this component horizontal scaling is prefered using `UPIPE_SIZE`

```
... UPIPE_SIZE=2 docker-compose up
```

### Example

- Spawning the client with 5 upipe and GPU support :
```
MAIN_ADDRESS=... UPIPE_SIZE=5 docker-compose -f docker-compose.yaml -f enable-gpu.yaml up -d
```

### Monitoring

### About it
> scrap -> upipe -> bpipe -> transactioneer
