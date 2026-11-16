1. Real-world automation scenarios
    - we'll examine the Bash implementation, and the equivalent Python implementation

2. JSON and YAML
    - Why structured data formats exist

3. Python ecosystem
    - venv, libraries, dependency management

4. Real application walkthrough - HW

-----


# A company manages servers across multiple environments. 
# We need to examine an inventory and identify servers that violate operational requirements.


prod - where you receive the traffic, application is live here (59 linux servers)

staging - (10 )

testing - (5)
dev - (4) 
dev0 - 10


inventoryt - db for your server info, diary for your server info, registry for your server info


inventory is generally created, maintained from cloud api, internal application handling


to handle or solve the scenario 1, bash provides a tool called jq - json processor tool


---

JSON AND YAMl

3 diff applications - 1. getting info about your servers - python
2. creating a report - java
3. compliance issues from this   - java/go

json and yaml
csv, xml


prod-api production ap-south-1 1 4 payments false true

{
  "name": "prod-api-02",
  "environment": "production",
  "cpu": 1,
  "memory_gb": 4,
  "owner": "payments",
  "backup_enabled": false
}

JSON - javascript object notation  (not limited to javascirpt)

use case: python cna internally work easily with python objects and then when finally time is to share this info with a new app/service , it can use .dumps() to change it to json and share it

json - interchangable fomrat


json

string, number, boolean, null, object(by object i mean key value pairs), array

afzaal.  1 2.    true, false null {"cpu":"4"} ["prod","production"]

json object xx==xx not the same thing as a python dictionary

server = {
    "name": "prod-api-02",
    "backup_enabled": False,
    "owner": None
}

{
  "name": "prod-api-02",
  "backup_enabled": false,
  "owner": null
}

python object ---> json.loads() converts into a jsonn object --> json.dumps() convert a json object into a python object(dictionary)


raw_data = Path("/data/inventory.json").read_text() string

type(raw_data) 


json.loads() - python object on which necessary processing can be done and again once the work is done, can be
transformed into json object and sent to the relevant dependent services


yaml

are defining config in a structured format 

(k8s, cicd pipelines)


monitoring tool - 1. which services should it monitor 2. how long to wait before monitoring again 
3. time outs 
4. what are the tries


variables are solving - there is no regular chagne in your app code


TIMEOUT_SECONDS = 2
MAX_ATTEMPTS = 5
MAX_LATENCY_MS = 500

config.yaml
----



{
defaults: {
  timeout_seconds: 2
  max_attempts: 3
  max_latency_ms: 500

services:
  - id: checkout-api
    owner: commerce
    critical: true
  - id: payments-api
    owner: payments
    critical: true
  - id: catalog-api
    owner: commerce
    critical: false
  - id: notification-worker
    owner: platform
    critical: true
  - id: identity-api
    owner: security
    critical: true


to handle functionalites that are not provided by the Python Standard Library , we use external libraries - how to get them? install them - using pip

pip /pip3

pip3 install pyYAML

to list modules that are installed/present in my python environment = help("modules")


pip/pip3 list - to list the installed packages/libraries


if i were to list the methods/functions == in general functionalites that a module offers 
use teh command dir(module name)


the help command - i have the module and the specific functionality from thsi module, and want info/instructiosn on how to use it, help(json.loads)


to get info on the specific library/package installed = pip show package_name


---
venv

project a - automation tool (tested this with version 1 of say library x) / specific version of python

project b - reporting tool (tested and works only with version 2 of say library x) / specif version 2 of python

python offers venv
creating venv =
 python3 -m venv .project1
with a diff version(3.12.16) python3.12 -m venv .project2

activate a virtual env
source .project1/bin/activate

deactivate - deactivates/comes out of the current virtual env

deleting a venv = deactivate it + remove the repo


dependency management - how to find all the relevant dependencies once adn for all - COMMAND IS pip freeze (EXPLORE)

