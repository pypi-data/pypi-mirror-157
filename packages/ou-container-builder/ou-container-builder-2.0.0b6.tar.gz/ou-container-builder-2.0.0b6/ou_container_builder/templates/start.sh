#!/bin/bash

set -e

sudo /bin/chown {{ image.user }}:100 /home/{{ image.user }}/{{ module.code }}-{{ module.presentation }}

{% if flags and flags.ou_container_content %}
ou-container-content startup
{% endif %}

if [[ ! -z "${JUPYTERHUB_API_TOKEN}" ]]; then
    export JUPYTERHUB_SINGLEUSER_APP='jupyter_server.serverapp.ServerApp'
    exec jupyterhub-singleuser --ip=0.0.0.0 --port 8888 --ServerApp.config_file /etc/jupyter/jupyter_server_config.py
else
    exec jupyter server --ip=0.0.0.0 --port 8888 --config /etc/jupyter/jupyter_server_config.py
fi

{% if flags and flags.ou_container_content %}
ou-container-content shutdown
{% endif %}
