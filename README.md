# Benchmark high workload


### Start the system

```sh
$ docker compose up -d
```

### Benchmark

```sh
$ wrk -t12 -c12 -d60s -s benchmark.lua http://localhost:8000/write
$ wrk -t12 -c12 -d60s -s benchmark.lua http://localhost:8000/write-redis
$ wrk -t12 -c12 -d60s -s benchmark.lua http://localhost:8000/write-rabbitmq
```
