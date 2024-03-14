## :gear: Customize 

##### 🧑‍🤝‍🧑 Horizontal Scaling (upipe/hoz.yaml)
- `upipe` stands for `unit_data_pipe` and GPU support is not recommended as the loading time exceeds the benefits. 
For this component horizontal scaling is prefered using `UPIPE_SIZE`
```
... UPIPE_SIZE=2 docker-compose -f docker-compose  up
```
##### ⚡ GPU Support (bpipe/gpu.yaml)
- `bpipe` stands for `batch_data_pipe` and GPU support is recommended for it.
```
... docker compose -f docker-compose.yaml -f ./gpu.yaml up -d
```
> note : we do not provide horizontal scaling options for bpipe as it is dificult to configure both GPU
> and horizontal scaling ([more about this](https://github.com/exorde-labs/Exorde-Client-Microservice-Mint/issues/1))

##### 📘 Example

- Spawning the client with 5 upipe and GPU support :
```
MAIN_ADDRESS=... UPIPE_SIZE=5 docker-compose -f docker-compose.yaml -f ./gpu.yaml -d
```
