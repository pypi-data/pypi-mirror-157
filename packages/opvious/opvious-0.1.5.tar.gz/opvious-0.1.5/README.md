# Opvious SDK

https://opvious.ai

## Quickstart

You'll first need an API access token. You can generate a new one at
https://console.opvious.dev/authorizations.

```py
import opvious

client = opvious.Client(ACCESS_TOKEN)

# Create a new model formulation
client.register_specification(
  formulation_name='my-model',
  source_text='...'
)

# Attempt to solve a formulation
solution = client.run_attempt(
  formulation_name='my-model',
  # inputs...
)
```

### Jupyter integration

From within a Jupyter notebook, you can register a specification directly from
Markdown cells:

```py
opvious.jupyter.save_specification(client=client, formulation_name='my-model')
```
