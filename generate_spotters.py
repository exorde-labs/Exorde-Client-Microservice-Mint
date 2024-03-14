
import requests

def fetch_parameters(repo):
    url = f"https://raw.githubusercontent.com/exorde-labs/{repo}/main/meta.json"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['parameters']:
            return data['parameters']
    if response.status_code == 404:
        return []
    else:
        raise Exception("An error occured while retrieving package metadata")


def fetch_repos(topic, organization):
    url = f"https://api.github.com/search/repositories?q=topic:{topic}+org:{organization}"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        repo_names = [item['full_name'].split('/')[1] for item in data['items']]
        return repo_names
    else:
        return []
repos = fetch_repos("exorde-spot-driver", "exorde-labs")

print("""
version: '3'

services:
""", end='')

for repo in repos:
    parameters = fetch_parameters(repo)
    print(f"""  
  {repo}:
    restart: always
    labels:
        - "network.exorde.monitor=true"
        - "network.exorde.service=spot"
    image: exordelabs/spot{repo}
    networks: exorde-network
    init: true
    deploy:
""", end='')
    print('      replicas: ${' + repo[:3] + ':-0}')
    if len(parameters) > 0:
        print('    environment:')
    for parameter in parameters:
        print(f"      - {parameter}" + "=${" + f"{parameter}" + "}")

print("""
networks:
  exorde-network:
    external: true
""")
