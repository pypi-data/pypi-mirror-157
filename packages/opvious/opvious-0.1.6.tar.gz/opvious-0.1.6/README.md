# Opvious SDK

https://opvious.ai

## Quickstart

First, to install this package:

```sh
pip install opvious
```

You'll then need an API access token. You can generate one at
https://console.opvious.dev/authorizations. Once you have it, you can
instantiate a client and call its method:

```py
import opvious

client = opvious.Client(ACCESS_TOKEN)

# Create a new model formulation
await client.register_specification(
  formulation_name='my-model',
  source_text='...'
)

# Attempt to solve a formulation
solution = await client.run_attempt(
  formulation_name='my-model',
  # inputs...
)
```

### Jupyter integration

From within a Jupyter notebook, you can register a specification directly from
all Markdown cells:

```py
import opvious.jupyter

opvious.jupyter.save_specification(client=client, formulation_name='my-model')
```
