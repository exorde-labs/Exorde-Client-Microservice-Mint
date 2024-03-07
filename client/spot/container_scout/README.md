# ContainerScout

## Introduction
ContainerScout is a dynamic Docker container discovery service designed to integrate seamlessly with Prometheus for real-time monitoring of containerized applications. By leveraging the aiohttp framework, ContainerScout efficiently fetches and exposes the current state of Docker containers, enabling Prometheus to automatically discover and monitor new or removed containers without manual configuration.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Docker and Docker Compose are installed on your system.

## Installation
To install ContainerScout, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/ContainerScout.git
   ```

2. Navigate to the ContainerScout directory:
   ```sh
   cd ContainerScout
   ```

3. Build the Docker container:
   ```sh
   docker build -t containerscout .
   ```

4. Run ContainerScout using Docker:
   ```sh
   docker run -d -p 8080:8080 containerscout
   ```

Alternatively, use Docker Compose to manage ContainerScout alongside Prometheus and other services. Add ContainerScout to your \`docker-compose.yml\`:

```yaml
services:
  containerscout:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

## Usage
After deployment, configure Prometheus to fetch targets from ContainerScout by adding the following job to your \`prometheus.yml\`:

```yaml
scrape_configs:
  - job_name: 'dynamic-containers'
    http_sd_configs:
      - url: 'http://containerscout:8080/targets'
        refresh_interval: 1m  \# Adjust as needed
```

ContainerScout will now automatically discover Docker containers and provide Prometheus with the necessary targets for monitoring.
