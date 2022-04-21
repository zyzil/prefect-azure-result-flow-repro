# AzureResult connection string reproduction

## Reproducing

### Setup env

1. `python -m venv .venv`
2. `. .venv/bin/activate`
3. `pip install -r requirements.txt`

### Setup server

1. `prefect server start`
2. `prefect backend server`
3. `prefect create project repro`

### Setup agent

1. `prefect agent docker start -l docker -e AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING`

### Scenarios and Results

1. `AZURE_STORAGE_CONNECTION_STRING` not available at registration
   1. `AZURE_STORAGE_CONNECTION_STRING` not available at runtime
      1. Nothing serialized to flow storage.
      2. Error at runtime: `ValueError('Azure connection string not provided. Set either directly with connection_string or via Prefect Secret using connection_string_secret parameter.')`

   2. `AZURE_STORAGE_CONNECTION_STRING` available at runtime
      1. Nothing serialized to flow storage.
      2. Error at runtime: `ValueError('Azure connection string not provided. Set either directly with connection_string or via Prefect Secret using connection_string_secret
        - The serialized `connection_string` value of `None` is used instead of loading at runtime

2. `AZURE_STORAGE_CONNECTION_STRING` available at registration (`. ./set-bad-conn-str.sh` used to export)
   1. `AZURE_STORAGE_CONNECTION_STRING` not available at runtime
      1. `AZURE_STORAGE_CONNECTION_STRING` environment variable that was set at registration is serialized to flow
      2. Serialized `connection_string` is used at runtime

   2. `AZURE_STORAGE_CONNECTION_STRING` available at runtime
      1. `AZURE_STORAGE_CONNECTION_STRING` environment variable that was set at registration is serialized to flow
      2. Serialized `connection_string` is used at runtime

### Register flow

1. `prefect register --project repro -p azure_result_flow.py -l docker`

### Observing connection string is serialized

For `azure_result_flow.py`

1.  `docker run -it azure-result-flow:<tag from build output> /bin/bash`
2.  `python`
3.  Paste code snippet to observe Flow's result
```python

import cloudpickle
from prefect.utilities import storage
with open("/opt/prefect/flows/azure-result-flow.prefect", "r") as flow_file:
    flow_bytes = flow_file.read().encode("utf-8")

flow = storage.flow_from_bytes_pickle(flow_bytes)
print(flow.result.connection_string)

```

4. Output:
```
>>> print(flow.result.connection_string)
DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=mystoragekey
```

For `azure_result_task.py`

1.  `docker run -it azure-result-task:<tag from build output> /bin/bash`
2.  `python`
3.  Paste code snippet to observe Flow's result
```python

import cloudpickle
from prefect.utilities import storage
with open("/opt/prefect/flows/azure-result-task.prefect", "r") as flow_file:
    flow_bytes = flow_file.read().encode("utf-8")

flow = storage.flow_from_bytes_pickle(flow_bytes)
get_word_task = next(t for t in flow.tasks if t.name == "get_word")
print(get_word_task.result.connection_string)


```

4. Output:
```
>>> get_word_task = next(t for t in flow.tasks if t.name == "get_word")
>>> print(get_word_task.result.connection_string)
DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=mystoragekey
```

### Running Flow

This example I have a bad connection string at registration and good connection string set for agent.

Results, bad connection string is used:

```
Unexpected error: ClientAuthenticationError("Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.
```
