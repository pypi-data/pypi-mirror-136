
# Context

RecordKeeper (abbreviated to RK) is aimed at two broad goals:

1. Explaining why something happened in your platform.
   Common example that we want to support is: why event X happened at time T?
   What Models were used? Who trained them, using training data ingested from which
   datasources? It achieves it by creating graph of events.

2. Recreating platform state at that time.

# Basics

RKClient library is used to create events (PEMS) and inform RK about them.

You will need a running RecordKeeper Event Receiver to be able to work with it.

Recommended usage:

```
emitter_id = uuid.UUID('..some static uuid..')
rk_host = os.environ.get('RK_HOST')

rk_client = RKClientFactory.get(rk_host, emitter_id)
```

By using factory, automatically when `RK_MOCK=true` env variable will be defined, 
the returned client will fake the connections and return only success codes. 

# Details

The Receiver will be configured with max PEM payload size. If your PEM exceeds 
this limit, it will be rejected (with explanation).

You can query for the PEM limit size in `get_info()`, in `pem_size_limit` field.


## RKClient from Python console

```
cd rkclient/
python3
>>> from rkclient import RKAdmin
>>> rk = RKAdmin('http://127.0.0.1:8082')
>>> pems, msg, ok = rk.get_pems()
>>> assert ok, msg
>>> for pem in pems:
>>>   print(pem)
```

---
RKClient is part of ERST Recordkeeper repository.

RKClient is licensed with GNU General Public License version 3 or later,
see LICENSE file for details.

Recordkeeper is ERST's implementation of the Context Cartographer specification.

