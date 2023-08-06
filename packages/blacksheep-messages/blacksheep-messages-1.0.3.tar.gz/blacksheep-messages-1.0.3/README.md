# BlackSheep-Messages
Extension for [BlackSheep](https://github.com/Neoteroi/BlackSheep) that similar with flask flashes message

```bash
pip install blacksheep-messages
```

## How to use (BlackSheep MVC)

First, set your web_url on settings.yaml

```yaml
app_name: Your Website
web_url: http://localhost:8000
```

Then, you can import BlackSheep Messages on server.py

```python
from app.configuration import load_configuration
from app.program import configure_application
from app.services import configure_services
from blacksheep_messages import use_blacksheep_message

if uvloop is not ...:
    uvloop.install()

app = configure_application(*configure_services(load_configuration()))
use_blacksheep_message(app, load_configuration())

```

After registering BlackSheep Messages, services are configured in the application, so they are automatically resolved in any request handler requiring a parameter named bs_message

```python

@post("/register")
async def register_action(bs_message):
    if True:
        bs_message.add("No Error", "success")
    else:
        bs_message.add("Error found", "error")

```

Than you can get message using `bs_message(category)` on jinja2 template

```jinja2
{% if bs_message("success", check=True) %}
	{% for msg in bs_message("success") %}
		{{ msg }}
	{% endfor %}
{% endif %}

{% if bs_message("error", check=True) %}
	{% for msg in bs_message("error") %}
		{{ msg }}
	{% endfor %}
{% endif %}
```

Note : set check value to True to avoid message deleted automatically.