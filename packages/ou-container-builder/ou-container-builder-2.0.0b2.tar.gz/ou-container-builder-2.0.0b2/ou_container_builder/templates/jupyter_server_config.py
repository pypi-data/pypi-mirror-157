# ####################
# Server configuration
# ####################

c.ServerApp.quit_button = False
c.ServerApp.trust_xheaders = True
c.ServerApp.tornado_settings = {
    'headers': {
        'Content-Security-Policy': "frame-ancestors 'self' https://vce.computing.edgehill.ac.uk",
        'Access-Control-Allow-Origin': 'https://vce.computing.edgehill.ac.uk',
    }
}
{% if server.access_token %}
c.ServerApp.token = '{{ server.access_token }}'
{% endif %}
c.ServerApp.default_url = '{{ server.default_path }}'
c.ServerApp.quit_button = False
c.ServerApp.iopub_data_rate_limit = 10000000

# ##########################
# Server proxy configuration
# ##########################

{% if web_apps %}
c.ServerProxy.servers = {
    {% for app in web_apps %}
    '{{ app.path }}': {
        'command': {{ app.cmdline }},
        {% if app.port %}
        'port': app.port,
        {% endif %}
        {% if app.timeout %}
        'timeout': {{ app.timeout }},
        {% endif %}
        {% if app.absolute_url %}
        'absolute_url': True,
        {% endif %}
    },
    {% endfor %}
}
{% endif %}


# ##############################
# Classic notebook configuration
# ##############################

c.NotebookApp.quit_button = False
