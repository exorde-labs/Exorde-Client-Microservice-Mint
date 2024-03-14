
# 📘 How to mine EXD
> The client is ran using two `docker compose` files.

## 1️⃣ Core
- `MAIN_ADDRESS` is specified as an ENV variable

### Example
```bash
MAIN_ADDRESS=... docker compose up -d
```
> [more parameters to buff the perf](./CUSTOMIZE.md)



## :two: Spotters

[`spotters.yaml`](./docker-compose.yaml)  provides an easy way to launch the different spotters with different redundancy parameters, each module is parametrable with it's three first leters (jumping over `spot`)

### Example

```shell
rss=2 docker compose up -d
```
Will launch two rss instances.


### :warning: Important
- There is **no orchestration mechanism** when you launch your spotters this way.
- They will be staticly launched and **the module distribution usage is 100% under your control.**
