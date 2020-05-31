docktor
-------

manage and run multiple tor containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _how-to:

how to...
~~~~~~~~~

...install
^^^^^^^^^^

.. code:: shell

   curl -sSL https://raw.githubusercontent.com/smthnspcl/docktor/master/install.sh | bash
   # or
   git clone https://github.com/smthnspcl/docktor
   cd docktor
   sudo python3 setup.py install

...use from cli
^^^^^^^^^^^^^^^

.. code:: shell

   $docktor --help
   usage: docktor [-h] [--host HOST] [--port PORT] [-i INSTANCES]
                  [--control-password CONTROL_PASSWORD]

   optional arguments:
     -h, --help            show this help message and exit
     --host HOST
     --port PORT
     -i INSTANCES, --instances INSTANCES
     --control-password CONTROL_PASSWORD

   ex:
   $docktor -i 2
   # runs 2 tor containers

   $curl http://127.0.0.1:1337/api/instances
   # should ouput something like this
   [
     {
       "id":"64b0cd480f6a9e1653d10556cf6c99138a2607b18f52415b0b60c6b7f75cdc4e",
       "short_id":"64b0cd480f",
       "name":"docktor-0",
       "status":"running",
       "ports":[
         {"8118\/tcp":"33038"},
         {"8123\/tcp":"33037"},
         {"9050\/tcp":"33036"},
         {"9051\/tcp":"33035"}
       ]
     },
     {
       "id":"5c0955a0f20c2b92e8bc2d3adcb663f8142a3878f5ba83657462c0bd4d430ff8",
       "short_id":"5c0955a0f2",
       "name":"docktor-1",
       "status":"running",
       "ports":[
         {"8118\/tcp":"33042"},
         {"8123\/tcp":"33041"},
         {"9050\/tcp":"33040"},
         {"9051\/tcp":"33039"}
       ]
     }
   ]

   # renew ip addresses for all containers
   curl http://127.0.0.1:1337/api/renew
   # renew ip address for one container
   curl http://127.0.0.1:1337/api/renew/docktor-0

...use from code
^^^^^^^^^^^^^^^^

.. code:: python

   from docktor import Manager
   manager = Manager(2)
   manager.start()
   manager.wait_until_ready()
   print(manager.get_containers())
   manager.stop()

notice:
~~~~~~~

if your code crashes you might need to stop the containers by hand
