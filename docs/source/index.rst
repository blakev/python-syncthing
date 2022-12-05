Welcome to python-syncthing's documentation!
============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

python-syncthing
================

Python bindings to the Syncthing REST interface.

- `Syncthing <https://syncthing.net/>`_
- `Syncthing REST Documentation <http://docs.syncthing.net/dev/rest.html>`_
- `Syncthing Forums <https://forum.syncthing.net/>`_
- `Pypi <https://pypi.python.org/pypi/syncthing>`_ (``syncthing``)

Reference
---------

- `Module`_
- `System Endpoints`_
- `Config Endpoints`_
- `Cluster Endpoints`_
- `Folder Endpoints`_
- `Database Endpoints`_
- `Events Endpoints`_
- `Statistic Endpoints`_
- `Misc. Endpoints`_
- `Debug Endpoints`_
- `Noauth Endpoints`_
- `Running Tests`_
- `License`_


Module
------

.. automodule:: syncthing
   :members:

System Endpoints
----------------

.. autoclass:: syncthing.System()
   :members:
   :undoc-members:

Config Endpoints
----------------

.. autoclass:: syncthing.Config()
   :members:
   :undoc-members:

Cluster Endpoints
-----------------

.. autoclass:: syncthing.Cluster()
   :members:
   :undoc-members:

Folder Endpoints
----------------

.. autoclass:: syncthing.Folder()
   :members:
   :undoc-members:

Database Endpoints
------------------

.. autoclass:: syncthing.Database()
   :members:
   :undoc-members:

Events Endpoints
----------------

.. autoclass:: syncthing.Events()
   :members:
   :undoc-members:

Statistic Endpoints
-------------------

.. autoclass:: syncthing.Statistics()
   :members:
   :undoc-members:

Misc. Endpoints
---------------

.. autoclass:: syncthing.Misc()
   :members:
   :undoc-members:

Debug Endpoints
---------------

.. autoclass:: syncthing.Debug()
   :members:
   :undoc-members:

Noauth Endpoints
----------------

.. autoclass:: syncthing.Noauth()
   :members:
   :undoc-members:


Running Tests
-------------

   The API doctests rely on the following function to run against your instance.
   None of the "breaking" calls will be tested. You must set the following environment
   variables otherwise all tests will fail.

   .. code::

      def _syncthing():
          KEY = os.getenv('SYNCTHING_API_KEY')
          HOST = os.getenv('SYNCTHING_HOST', '127.0.0.1')
          PORT = os.getenv('SYNCTHING_PORT', 8384)
          IS_HTTPS = bool(int(os.getenv('SYNCTHING_HTTPS', '0')))
          SSL_CERT_FILE = os.getenv('SYNCTHING_CERT_FILE')
          return Syncthing(KEY, HOST, PORT, 10.0, IS_HTTPS, SSL_CERT_FILE)


License
-------

   The MIT License (MIT)

   Copyright (c) 2015-2016 Blake VandeMerwe

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
