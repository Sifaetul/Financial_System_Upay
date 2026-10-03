import yaml

with open('docker-compose.yml', 'r') as f:
    compose = yaml.safe_load(f)

# Optional: remove exposed ports from backend and frontend if we strictly want nginx to be the only entrypoint.
# But for now, just add nginx.
compose['services']['nginx'] = {
    'image': 'nginx:alpine',
    'ports': ['80:80'],
    'volumes': ['./nginx/nginx.conf:/etc/nginx/nginx.conf:ro'],
    'depends_on': ['frontend', 'backend']
}

with open('docker-compose.yml', 'w') as f:
    yaml.dump(compose, f, sort_keys=False)
