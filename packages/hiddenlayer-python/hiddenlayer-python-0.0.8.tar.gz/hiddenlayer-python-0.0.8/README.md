# HiddenLayer

    HiddenLayer's python tools and clients





## Install

    pip3 install hiddenlayer-python

---

### HiddenLayerClient

    Client to interact with the HiddenLayer API

#### Create client
```python3
from hiddenlayer.clients import HiddenLayerClient

# token can also be set via HL_API_TOKEN environment variable
client = HiddenLayerClient(token="<API-TOKEN>")

print(client.health())
{'title': 'HiddenLayer-API caml', 'version': '1', 'status': 'ok'}
```

#### Get event
```python3
from hiddenlayer.clients import HiddenLayerClient

client = HiddenLayerClient(token="<API-TOKEN>")

client.get_event("be1b191d-99a3-4d38-915a-e2d8361184ef")
{'customer_id': '977399c5-24b9-4145-b165-a17b700cdafe',
 'sensor_id': 'test_model',
 'requester_id': 'hl-test',
 'event_id': 'be1b191d-99a3-4d38-915a-e2d8361184ef',
 'event_time': '2022-06-13T22:33:21.077624',
 'vector_sha256': '583dbc41a4e0826e4b2dbede6760bc80fe58ddc682b66cfba1e985a6538bc19e',
 'prediction': 0.6740969506920719}
```

#### Get list of events

These are the current filters that can be used when getting list of events

    sensor_id: filter by sensor_id
    requester_id: filter by requester_id
    group_id: filter by group_id
    input_layer_exponent_sha256: filter by the input_layer exponent sha256
    input_layer_byte_size: filter by input_layer size in bytes
    input_layer_dtype: filter by input_layer data type
    output_layer_byte_size: filter by input_layer size in bytes
    output_layer_dtype: filter by input_layer data type
    event_start_time: start date for filtering by event_time
    event_stop_time: stop date for filtering by event_time

```python3
from hiddenlayer.clients import HiddenLayerClient

client = HiddenLayerClient(token="<API-TOKEN>")

# filter by requester_id, event_id, event_start_time, and event_stop_time
client.get_events(max_results=50) # default 1000 max results
[{'customer_id': '977399c5-24b9-4145-b165-a17b700cdafe',
  'sensor_id': 'test_model',
  'requester_id': 'hl-test',
  'event_id': '8ea48083-9bcb-4266-9b9b-04857984a6a3',
  'event_time': '2022-06-14T13:42:56.377004',
  'vector_sha256': '239ef13cc1e15952c682483452f674ffc7cd81c81df589f369a7c63e3c79e7fa',
  'prediction': 0.7731156403121537},
 {'customer_id': '977399c5-24b9-4145-b165-a17b700cdafe',
  'sensor_id': 'test_model',
  'requester_id': 'hl-test',
  'event_id': '60c5ea87-0c46-4822-9f09-6c8e3bfb42c7',
  'event_time': '2022-06-14T13:42:56.236905',
  'vector_sha256': 'f0726b2832608f9497880071447f89bd38948dbf0a0f510bac13a2f0cf3995cf',
  'prediction': 0.3811970489679117},
 ...
]
```

#### Get event count
```python3
client.get_event_count()
```

#### Get alert

    Same functionality as retrieving an event


#### Get list of alerts

    Same functionality as retrieving a list of events

These are the current filters that can be used when getting list of events and alerts

    sensor_id: filter by sensor_id
    requester_id: filter by requester_id
    group_id: filter by group_id
    category: category of alert
    tactic: mitre tactic of alert
    risk: risk of alert
    event_start_time: start date for filtering by event_time
    event_stop_time: stop date for filtering by event_time


#### Get alert count
```python3
client.get_alert_count()
```

#### Get vector
```python3
from hiddenlayer.clients import HiddenLayerClient

client = HiddenLayerClient(token="<API-TOKEN>")

client.get_vector("583dbc41a4e0826e4b2dbede6760bc80fe58ddc682b66cfba1e985a6538bc19e")
[0.3272676394984871,
 -0.05370468579134668,
 0.6139997822625176,
 0.44721997994737894,
 -0.40397475858578435,
 0.3085298917492199,
 0.3074662380624216,
 0.17759178808034304,
 -0.928663757835657,
 -1.5372852813486815,
 1.2085312691167172,
 0.8254611710240448,
 0.5828129933899114,
 -0.4512473641489139,
 0.8993772725829033,
 -0.6835656184552312,
 -0.6372820530521444,
 -0.6756563609649021,
 0.27037660324157103,
 0.3773093202476495]
```

#### Submit vectors and predictions for a model
```python3
from sklearn.datasets import make_classification

from hiddenlayer.clients import HiddenLayerClient

client = HiddenLayerClient(token="<API-TOKEN>")

x, y = make_classification(2) # x is the vectors
predictions = [0.7731156403121537, 0.3811970489679117] # OPTIONAL

client.submit("test_model_v1", "requester_abc123", x, y, predictions)
{'sensor_id': 'test_model_v1',
 'event_time': '2022-06-15T03:07:50.688627',
 'customer_id': '977399c5-24b9-4145-b165-a17b700cdafe',
 'event_id': '5119bcc9-18de-4115-a8e2-528f6b904108',
 'requester_id': 'requester_abc123'}
```