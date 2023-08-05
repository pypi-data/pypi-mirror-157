# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cr_api_client', 'cr_api_client.topology', 'cr_api_client.topology.validator']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.3,<2.12.0',
 'argcomplete>=1.12.1,<1.13.0',
 'colorama>=0.4.4,<0.5.0',
 'humanize>=3.13.1,<4.0.0',
 'loguru>=0.5.3,<0.6.0',
 'markupsafe==2.0.1',
 'pydantic>=1.9.1,<1.10.0',
 'pypsrp>=0.5.0,<0.6.0',
 'requests>=2.24.0,<3.0.0',
 'ruamel.yaml>=0.16.10,<0.17.0',
 'setuptools==44.0.0',
 'termcolor>=1.1.0,<1.2.0']

entry_points = \
{'console_scripts': ['cyber_range = cr_api_client.cyber_range:main']}

setup_kwargs = {
    'name': 'cr-api-client',
    'version': '1.10.0',
    'description': 'AMOSSYS Cyber Range client API',
    'long_description': '# AMOSSYS Cyber Range client API\n\n## Installation\n\nNote: it is recommanded to install the package in a virtualenv in order to avoid conflicts with version dependencies of other packages.\n\n```sh\npython3 setup.py install\n```\n\n## Configuration\n\nAccess to the Cyber Range is possible with either of the following configuration methods.\n\n### Configuration through configuration file (CLI only)\n\nIt is possible to configure access to the Cyber Range through a configuration file, specified with the `--config` command line parameter:\n\n```sh\n$ cyber_range --help\n(...)\n--config CONFIG       Configuration file\n(...)\n```\n\nConfiguration file content should be of the form `--key = value` (without quotes in values), as in the following exemple:\n\n```\n[DEFAULT]\n--core-url = https://[CORE-URL-API]\n--scenario-url = https://[SCENARIO-URL-API]\n--provisioning-url = https://[PROVISIONING-URL-API]\n--redteam-url = https://[REDTEAM-URL-API]\n--cacert = <PATH TO CA CERT>\n--cert = <PATH TO CLIENT CERT>\n--key = <PATH TO CLIENT PRIVATE KEY>\n```\n\n### Configuration through command line arguments (CLI only)\n\nIt is possible to configure access to the Cyber Range through command line arguments. See `cyber_range --help` command line output for available parameters:\n\n```sh\n$ cyber_range --help\n(...)\n  --core-url CORE_API_URL\n                        Set core API URL (default: \'http://127.0.0.1:5000\')\n  --scenario-url SCENARIO_API_URL\n                        Set scenario API URL (default: \'http://127.0.0.1:5002\')\n  --provisioning-url PROVISIONING_API_URL\n                        Set provisioning API URL (default: \'http://127.0.0.1:5003\')\n  --redteam-url REDTEAM_API_URL\n                        Set redteam API URL (default: \'http://127.0.0.1:5004\')\n  --cacert CACERT       Set path to CA certs\n  --cert CERT           Set path to client cert\n  --key KEY             Set path to client key\n```\n\n### Configuration through programmatic means\n\nIt is possible to configure access to the Cyber Range programmatically in Python:\n\n```python\nimport cr_api_client.core_api as core_api\nimport cr_api_client.scenario_api as scenario_api\nimport cr_api_client.provisioning_api as provisioning_api\nimport cr_api_client.redteam_api as redteam_api\n\n# Set URL API\ncore_api.CORE_API_URL = "https://[CORE-URL-API]"\nscenario_api.SCENARIO_API_URL = "https://[SCENARIO-URL-API]"\nprovisioning_api.PROVISIONING_API_URL = "https://[PROVISIONING-URL-API]"\nredteam_api.REDTEAM_API_URL = "https://[REDTEAM-URL-API]"\n\n# Set server and client certificates for Core API\ncore_api.CA_CERT_PATH = <PATH TO CA CERT>\ncore_api.CLIENT_CERT_PATH = <PATH TO CLIENT CERT>\ncore_api.CLIENT_KEY_PATH = <PATH TO CLIENT PRIVATE KEY>\n\n# Apply same server and client certificates to other API\nredteam_api.CA_CERT_PATH = provisioning_api.CA_CERT_PATH = scenario_api.CA_CERT_PATH = core_api.CA_CERT_PATH\nredteam_api.CLIENT_CERT_PATH = provisioning_api.CLIENT_CERT_PATH = scenario_api.CLIENT_CERT_PATH = core_api.CLIENT_CERT_PATH\nredteam_api.CLIENT_KEY_PATH = provisioning_api.CLIENT_KEY_PATH = scenario_api.CLIENT_KEY_PATH = core_api.CLIENT_KEY_PATH\n```\n\n## CLI usage\n\nSee `cyber_range --help` command line output for available parameters:\n\n```sh\n$ cyber_range --help\n(...)\n```\n\n## Programmatic usage\n\n### Platform initialization API\n\nBefore starting a new simulation, the platform has to be initialized:\n\n```python\ncore_api.reset()\nredteam_api.reset_redteam()\n```\n\n### Simulation API\n\n```python\n# Create a simulation from a topology\ncore_api.create_simulation_from_topology(topology_file: str)\n\n# Create a simulation from a basebox ID\ncore_api.create_simulation_from_basebox(basebox_id: str)\n\n# Start the simulation, with current time (by default) or time where the VM was created (use_vm_time=True)\ncore_api.start_simulation(id_simulation: int, use_vm_time: bool)\n\n# Pause a simulation (calls libvirt suspend API)\ncore_api.pause_simulation(id_simulation: int)\n\n# Unpause a simulation (calls libvirt resume API)\ncore_api.unpause_simulation(id_simulation: int)\n\n# Properly stop a simulation, by sending a shutdown signal to the operating systems\ncore_api.halt_simulation(id_simulation: int)\n\n# Stop a simulation through a hard reset\ncore_api.destroy_simulation(id_simulation: int)\n\n# Clone a simulation and create a new simulation, and return the new ID\ncore_api.clone_simulation(id_simulation: int) -> int\n\n# Mirror all network traffic through a local network interface\ncore_api.tap_simulation(id_simulation: int, iface: str, pcap: bool, filter: str)\n\n# Stop mirroring all network traffic\ncore_api.untap_simulation(id_simulation: int)\n\n# Delete a simulation in database\ncore_api.delete_simulation(id_simulation: int)\n```\n\n### Provisioning API\n\n```python\n# Apply provisioning configuration defined in YAML file on simulation defined in argument ID OR on machines defined in file\n# ``wait`` parameter defines if the function wait for task to complete or not.\n\nprovisioning_execute(id_simulation: int = None,\n                     machines_file: str = None,\n                     provisioning_file: str,\n                     debug: bool = False,\n                     wait: bool = True,\n                     ) -> Tuple[bool, str]:\n\n# Apply ansible playbooks on specified target(s):\n# ``wait`` parameter defines if the function wait for task to complete or not.\n\ndef provisioning_ansible(id_simulation: int = None,\n                         machines_file: str = None,\n                         playbook_path: str = None,\n                         target_roles: List[str] = [],\n                         target_system_types: List[str] = [],\n                         target_operating_systems: List[str] = [],\n                         target_names: List[str] = [],\n                         extra_vars: str = None,\n                         debug: bool = False,\n                         wait: bool = True,\n                         ) -> Tuple[bool, str]:\n\n# Get status on targeted simulation\nprovisioning_api.provisioning_status(id_simulation: int)\n\n# Get provisioning result on targeted simulation\nprovisioning_api.provisioning_result(id_simulation: int)\n```\n\n### Scenario API\n\n```python\nscenario_api.scenario_play(id_simulation: int, scenario_path: str,\n                              debug_mode: str = \'off\', speed: str = \'normal\',\n                              scenario_file_results: str = None)\n```\n\nThis method makes it possible to play  scenario defined in ``scenario path`` on simulation defined in ``id_simulation``.\nThese parameters are **mandatory**.\n\nThe following parameters are optional:\n\n* ``debug_mode``: This parameter has to be used for **debug** only. It corresponds to the level of verbosity of the debug traces generated during the execution of user actions:\n  * ``\'off\'``: no debug traces,\n  * ``\'on\'``:  with debug traces,\n  * ``\'full\'``: with maximum debug traces.\n\n  The default is ``\'off\'``. Debug traces are generated **on the server side only**.\n\n* ``speed``: This parameter affects the speed of typing keys on the keyboard and the speed of mouse movement:\n  * ``\'slow\'``: slow speed,\n  * ``\'normal\'``:  normal speed,\n  * ``\'fast\'``: fast speed.\n\n  The default is ``\'normal\'``.\n\n* ``scenario_file_results``: This parameter makes it possible to get the scenario results (of user actions) in a file.\n  Results are stored using a json format. The file name should be absolute (``\'/tmp/results.json\'`` for example).\n\n  Here an example:\n\n  ```json\n  {\n    "success": true,\n    "scenario_results": [\n        {\n            "name": "scenario.py",\n            "success": true,\n            "target": {\n                "name": "CLIENT1",\n                "role": "client",\n                "basebox_id": 70,\n                "ip_address": "localhost",\n                "vnc_port": 5901\n            },\n            "action_packs": {\n                "operating_system": "operating_system/windows7"\n            },\n            "action_list": [\n                {\n                    "name": "open_session",\n                    "parameters": {\n                        "password": "7h7JMc67",\n                        "password_error": "false",\n                        "login": "John"\n                    },\n                    "start_time": "2021-03-01 12:39:25.119",\n                    "end_time": "2021-03-01 12:39:57.325",\n                    "success": true,\n                    "implemented": true\n                },\n                {\n                    "name": "close_session",\n                    "parameters": {},\n                    "start_time": "2021-03-01 12:40:02.330",\n                    "end_time": "2021-03-01 12:40:09.303",\n                    "success": true,\n                    "implemented": true\n                }\n            ]\n        }\n    ]\n  }\n  ```\n\nHere are some examples of calling this method:\n\n```python\nscenario_api.scenario_play(1, \'./scenarios/my_scenario\') # this is the common way\n\nscenario_api.scenario_play(1, \'./scenarios/my_scenario\', scenario_file_results=\'/tmp/results.json\')\n\nscenario_api.scenario_play(1, \'./scenarios/my_scenario\', debug_mode=\'full\', speed=\'fast\')\n```\n\n### Redteam API\n\n```python\nredteam_api.execute_scenario(attack_list: str)\n```\n\nThis method executes sequentially each attack in list.\nFor each attack this method displays started time and ending time (last_update).\n\n```python\nredteam_api.execute_attack_name(attack_name: str,  waiting_worker: bool = True)\n```\n\nThis method execute one attack, selected by name.\n\n```python\ndef init_knowledge(data: List[dict])\n```\n\nLoad data into knowledge database.\n\nExample :\n```\n[\n  {"software":\n    {"host_ip": "192.168.33.11",\n    "software": {"category": "os"},\n    "credentials":[{"username": "Administrateur", "password": "Beezh35;"}]\n    }\n  }\n]\n```\n\n```python\ndef attack_infos(id_attack: str)\n```\n\nGet status and output for attack.\n\nExample :\n```\nstatus = "success",\noutput = [\n  {\n  "attack_session": {\n   "idAttackSession": 1,\n   "source": "vffxlcationgreedinessb.com",\n   "type": "powershell",\n   "identifier": "d67672cb-8f64-420a-a7ba-1d33d7b7fd45",\n   "privilege_level": 1,\n   "idHost": 1\n  }\n }\n]\n\n```\n\n```python\nredteam_api.list_workers()\n```\n\nThis method list all workers availabe in platform.\nList of attributes :\n* stability\n* reliability\n* side_effect\n* killchain_step : step in MITRE ATT&CK killchain\n\n```json\n{\n  "worker_id":"1548_002_001",\n  "name":"uac_bypass",\n  "description":"Use Metasploit uac bypass",\n  "stability":"CRASH_SAFE",\n  "reliability":"ALWAYS",\n  "side_effect":"NETWORK_CONNECTION",\n  "killchain_step":"privilege_escalation",\n  "repeatable":false\n}\n```\n\n\n```python\nredteam_api.list_attacks()\n```\n\nThis method return all attack (available, successed or failed) with time information and origin.\nList of attributes :\n* idAttack : Identifier for attack action\n* status : Attack status (failed, success or runnable)\n* created_date\n* started_date\n* last_update : End time\n* values : Values send to the worker\n* output : Data generated by this attack\n* source: idAttack that created it\n\nHere an example :\n```json\n{\n  "idAttack":13,\n  "worker":\n  {\n    "worker_id":"1548_002_001",\n    "name":"uac_bypass",\n    "description":"Use Metasploit uac bypass",\n    "stability":"FIRST_ATTEMPT_FAIL",\n    "reliability":"ALWAYS",\n    "side_effect":"NETWORK_CONNECTION",\n    "killchain_step":"privilege_escalation",\n    "repeatable":false\n    },\n  "status":"success",\n  "created_date":"2021-04-21 10:33:00",\n  "started_date":"2021-04-21 10:37:04",\n  "last_update":"2021-04-21 10:37:06",\n  "values":"{\\"Host.ip\\": \\"192.168.2.101\\", \\"AttackSession.type\\": \\"windows/x64/meterpreter/reverse_tcp\\", \\"AttackSession.source\\": \\"192.168.2.66\\", \\"AttackSession.identifier\\": \\"1\\"}",\n  "output": "",\n  "source":1}\n```\n\n\n*In progress*\n',
    'author': 'AMOSSYS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
