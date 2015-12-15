# python-syncthing

[![downloads/month](https://img.shields.io/pypi/dm/syncthing.svg?style=flat)](https://pypi.python.org/pypi/syncthing)
![version 1.0.0](https://img.shields.io/badge/version-1.0.0-orange.svg)

Python bindings to the Syncthing REST interface.

- [Syncthing](https://syncthing.net/)
- [Syncthing REST Documentation](http://docs.syncthing.net/dev/rest.html)
- [Syncthing Forums](https://forum.syncthing.net/)

### Installation

```bash
pip install syncthing
```

The main interface `Syncthing` provides access to all of the underlying endpoints. They're divided the same as the documentation, in categories: `sys` (`system`), `db` (`database`), `stats`, `misc`. All `GET` methods are available as immediate function calls, and `POST` methods via **`sync.CATEGORY.set.COMMAND()`** (for example, `sync.sys.set.config(..)`).

### Usage

```python
from syncthing import Syncthing

sync = Syncthing(api_key='xxxxabcdef', port=8384)

print(sync.sys.config())
```

#### Deferred Instantiation

```python

sync = Syncthing()
...
...
sync.init(api_key='...')
```

#### Instance Values

Both the `syncthing.Syncthing` and `syncthing.Interface` objects take the same `__init__` parameters. `Syncthing` provides getter/setter methods for the REST api that direct all communication through the `Interface` instance. An `Interface` object could interact with Syncthing directly by passing endpoints to the `do_req` method.

- `api_key`: **required**
- `host`: *localhost*
- `port`: *8080*
- `timeout`: *3.5* (seconds)
- `is_https`: *False*
- `ssl_cert_file`: *None*


#### GET Methods

```python
conf = sync.sys.config()
logs = sync.sys.log()
db_status = sync.db.status()
```

#### POST Methods

```python
sync.sys.set.restart()
sync.db.set.scan(folder='desktop_home')
```

### License

> The MIT License (MIT)
> 
> Copyright (c) 2015-2016 Blake VandeMerwe
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
