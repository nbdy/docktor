## docktor
#### manage and run multiple tor containers

```shell script
$python3 docktor.py --help
usage: docktor.py [-h] [--host HOST] [--port PORT] [-i INSTANCES]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST
  --port PORT
  -i INSTANCES, --instances INSTANCES

ex:
$python3 docktor.py -i 4
# runs 4 containers with tor

curl http://127.0.0.1:1337/api/instances
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
```