# python-syncthing

Python bindings to the Syncthing REST interface. Supports Python 2 and Python 3 (via [six](http://pythonhosted.org//six/)).

[Syncthing](https://syncthing.net/)

[Syncthing REST Documentation](https://github.com/syncthing/syncthing/wiki/REST-Interface)

```bash
pip install syncthing
```

These bindings use Meta classes to create dynamic bindings based on the latest documentation of the Synthing REST API on their github repository.

`GET` methods are returned as a Bunch dot-dictionary, and are bound to the `Syncthing` object as properties. `POST` calls are bound as methods to `Syncthing`,
beginning with the word `set_`, and allow arguments to be passed similarly as they would in the HTTP header.

## Quickstart

```python
from syncthing import Interface, Syncthing

sync_interface = Interface(
    'my api key',
    host = 'localhost',
    port = 'syncthing port',
    timeout = 5.0,            # seconds
    is_https = False
)

sync = Syncthing(sync_interface)

print(sync.methods)           # prints out the available REST methods

print(sync.warning_methods)   # REST methods that require force=True to perform

print(sync.help('db_browse')) # returns the documentation for a given method

```

### syncthing.Interface

#### Interface(api_key, host='localhost', port=8080, timeout=3.0, is_https=False, ssl_cert_file=None, **kwargs)

#### Interface.root
Returns the connection string given the initialization parameters, ie: `http://localhost:5324`

#### Interface.is_connected
Returns `True` if the Interface can communicate with the Syncthing server, `False` otherwise.

#### Interface.from_dict(d)
Returns an Interface from a dictionary config.

#### Interface.from_json(json_str)
Returns an Interface from a JSON string.

#### Interface.to_json()
Exports Interface configuration as JSON string.

### syncthing.Syncthing