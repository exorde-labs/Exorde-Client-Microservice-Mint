"""
Initially this code has been written to help prometheus detect targets to scrap.

It evolved as a component of the stack with the "get" endpoint which is used by
scrapers to determin which upipe they should send data to. This avoids providing
the volume access for docker api to containers that are horizontaly scaled.
"""
import logging
from aiohttp import web
import docker
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def fetch_docker_targets():
    logging.info("Fetching Docker targets...")
    # Fetch and parse the FILTER environment variable
    filter_env = os.getenv('FILTER', '')  # Example format: "com.example.department:IT"
    filter_key, filter_value = filter_env.split(':', 1) if ':' in filter_env else (None, None)

    client = docker.from_env()
    targets = []
    for container in client.containers.list():
        container_labels = container.labels  # Fetch labels for filtering
        # Skip containers that don't match the filter criteria, if any
        if filter_key and filter_value and not container_labels.get(
            filter_key
        ) == filter_value:
            continue  # Skip this container as it doesn't match the filter

        networks = container.attrs['NetworkSettings']['Networks']
        ip = None
        for network_name, network_details in networks.items():
            if 'IPAddress' in network_details and network_details['IPAddress']:
                ip = network_details['IPAddress']
                break  # Break after finding the first network with an IP

        if ip:
            port = "8000"  # Adjust with your actual port
            # Only include the job label here, as per requirements
            prometheus_labels = {"__meta_prometheus_job": container.labels.get(
                "com.docker.compose.service", "unknown_service")
            }
            # Format the target as specified
            targets.append({
                "labels": prometheus_labels, "targets": [f"{ip}:{port}"]
            })
        else:
            logging.warning(f"No IP found for container {container.id}")

    logging.info("Targets fetched successfully.")
    return targets

async def handle_targets(request):
    targets = await fetch_docker_targets()  # Your existing function to fetch targets
    response = web.json_response(targets)
    response.headers['Content-Type'] = 'application/json'  # Ensure correct Content-Type
    return response

async def fetch_ips_by_label(filter_key, filter_value):
    logging.info("Fetching IPs by label...")
    client = docker.from_env()
    ips = []
    for container in client.containers.list():
        container_labels = container.labels
        logging.info(f"Looking at {container} with {container_labels}")
        if filter_key and filter_value and container_labels.get(filter_key) == filter_value:
            networks = container.attrs['NetworkSettings']['Networks']
            if networks:
                for network_details in networks.values():
                    if 'IPAddress' in network_details and network_details['IPAddress']:
                        ips.append(network_details['IPAddress'])
                        break  # Assuming you want just one IP per container
    logging.info("IPs fetched successfully.")
    return ips

async def handle_ips_by_label(request):
    # Extract the filter from the query parameters
    query_params = request.query
    if query_params:
        filter_key, filter_value = list(query_params.items())[0]  # Assumes a single filter key-value pair
        logging.info(f"Filter_key is = {filter_key}, filter_value is = {filter_value}")
        ips = await fetch_ips_by_label(filter_key, filter_value)
        return web.json_response(ips)
    else:
        return web.json_response({"error": "No filter provided"}, status=400)


app = web.Application()
app.add_routes([web.get('/targets', handle_targets)])
app.add_routes([web.get('/get', handle_ips_by_label)])

if __name__ == '__main__':
    logging.info("Starting ContainerScout service on port 8080...")
    web.run_app(app, port=8080)

