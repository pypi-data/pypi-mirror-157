# ####################
# Server configuration
# ####################

c.ServerApp.quit_button = False
c.ServerApp.trust_xheaders = True
{% if server.wrapper_host %}
c.ServerApp.tornado_settings = {
    'headers': {
        'Content-Security-Policy': "frame-ancestors 'self' {{ server.wrapper_host }}",
        'Access-Control-Allow-Origin': '{{ server.wrapper_host }}',
    }
}
{% endif %}
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
