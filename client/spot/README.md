# Exorde Spotting

| container | image | has models | Image size | description | GPU Support |
| --- | --- | --- | --- | --- | --- |
| transactioneer | transactioneer | no | 1.25 G | Web3 interaction | not required |
| bpipe | bpipe | yes | 14.6 G | Batch processing | yes (recomended) |
| upipe | upipe | yes | 19.7 G | Unit processing | yes (not recomended) |
| scraper | scraper | no | 2.24 G | Data retrieval | not required |



# How to run

- `MAIN_ADDRESS` is specified as an ENV variable

```bash
MAIN_ADDRESS=... docker compose up -d
```

# About it
> scrap -> upipe -> bpipe -> transactioneer
