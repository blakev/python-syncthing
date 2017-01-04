.. python-syncthing documentation master file, created by
   sphinx-quickstart on Tue Jan  3 16:17:40 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

python-syncthing
================

Python bindings to the Syncthing REST interface.

.. toctree::
   :caption: Contents

Module
------

.. automodule:: syncthing
   :members:

System Endpoints
----------------

.. autoclass:: syncthing.System()
   :members:
   :undoc-members:

Database Endpoints
------------------

.. autoclass:: syncthing.Database()
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