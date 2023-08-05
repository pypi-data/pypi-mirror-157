#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import json
import os
import shutil
import time
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import requests
from humanize import naturalsize
from loguru import logger
from ruamel.yaml import YAML


# Configuration access to Cyber Range endpoint
CORE_API_URL = "http://127.0.0.1:5000"
# Expect a path to CA certs (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CA_CERT_PATH = None
# Expect a path to client cert (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_CERT_PATH = None
# Expect a path to client private key (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_KEY_PATH = None


# Simulation status mapping
map_status = {
    "CREATED": 1,
    "PREPARING": 2,
    "READY": 3,
    "STARTING": 4,
    "PROVISIONING": 5,
    "RUNNING": 6,
    "SCENARIO_PLAYING": 7,
    "STOPPING": 8,
    "DESTROYED": 9,
    "CLONING": 10,
    "PAUSING": 11,
    "UNPAUSING": 12,
    "PAUSED": 13,
    "ERROR": 14,
}


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: Any) -> requests.Response:
    return requests.get(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _post(route: str, **kwargs: Any) -> requests.Response:
    return requests.post(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _put(route: str, **kwargs: Any) -> requests.Response:
    return requests.put(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _delete(route: str, **kwargs: Any) -> requests.Response:
    return requests.delete(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _handle_error(result: requests.Response, context_error_msg: str) -> None:
    if (
        result.headers.get("content-type") == "application/json"
        and "message" in result.json()
    ):
        error_msg = result.json()["message"]
    else:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


def _simulation_execute_operation(
    operation: str,
    id_simulation: int,
    operation_status: str,
    optional_param: Optional[Any] = None,
) -> str:
    """Generic method to launch API operation on a target simulation."""

    logger.info(
        "[+] Going to execute operation '{}' on simulation ID '{}'".format(
            operation, id_simulation
        )
    )

    # Build URI
    uri = f"/simulation/{id_simulation}/{operation}"
    if optional_param is not None:
        uri = f"{uri}/{str(optional_param)}"

    # Request URI
    result = _get(uri)
    if result.status_code != 200:
        _handle_error(result, "Cannot execute operation '{operation}'")

    # Handle cloning case where a new id_simulation or new dataset_id is returned
    if operation == "clone":
        id_simulation = result.json()["id"]

    # Wait for the operation to be completed in backend
    current_status = ""
    while True:
        # Sleep before next iteration
        time.sleep(2)

        logger.info(
            "  [+] Currently executing operation '{}' on "
            "simulation ID '{}'...".format(operation, id_simulation)
        )

        simulation_dict = fetch_simulation(id_simulation)

        current_status = simulation_dict["status"]

        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation operation: '{}'".format(error_message)
            )
        elif current_status != operation_status:
            # Operation has ended
            break

    logger.info(
        "[+] Operation '{}' on simulation ID '{}' was correctly executed".format(
            operation, id_simulation
        )
    )
    logger.info("[+] Current simulation status: '{}'".format(current_status))

    return id_simulation


def _reset_database() -> Any:
    """Reset the database (clean tables) and
    re-populate it with static info (baseboxes, roles...)
    """
    result = _delete("/database/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    return result.json()


def _reset_virtclient() -> Any:
    """Ask to stop virtclient VMs."""
    result = _get("/simulation/virtclient_reset")

    if result.status_code != 200:
        _handle_error(result, "Cannot reset virtclient")

    return result.json()


def _validate_yaml_topology_file(yaml_configuration_file: str) -> None:
    if os.path.exists(yaml_configuration_file) is not True:
        raise Exception(
            "The provided YAML configuration path does not exist: '{}'".format(
                yaml_configuration_file
            )
        )

    if os.path.isfile(yaml_configuration_file) is not True:
        raise Exception(
            "The provided YAML configuration path is not a file: '{}'".format(
                yaml_configuration_file
            )
        )

    if os.access(yaml_configuration_file, os.R_OK) is not True:
        raise Exception(
            "The provided YAML configuration file is not readable: '{}'".format(
                yaml_configuration_file
            )
        )


def _read_yaml_topology_file(yaml_configuration_file: str) -> str:
    with open(yaml_configuration_file, "r") as fd:
        yaml_content = fd.read()
        return yaml_content


def _zip_resources(resources_path: Path, temp_dir: Path) -> Path:
    """
    Zip a folder in an archive
    """
    dir_name: str = os.path.basename(os.path.normpath(resources_path))
    zip_base_name: str = os.path.join(temp_dir, dir_name)
    zip_format: str = "zip"
    shutil.make_archive(
        base_name=zip_base_name, format=zip_format, root_dir=resources_path
    )
    return "{}.zip".format(zip_base_name)


# Modify the topology to add parameters that can be deduced by
# reading the topology
def _simu_create_add_implicit_topo_parameters(topology: Any) -> None:
    # Add a "dns" parameter to docker nodes by deducing it from
    # reading the "dhcp_nameserver" of router nodes
    _simu_create_add_implicit_dns_parameter(topology)


def _simu_create_add_implicit_dns_parameter(topology: Any) -> None:
    # List the DNS servers and their switches
    switch_name_to_dns_ip = dict()
    for link in topology["links"]:
        if "type" not in link["node"]:
            continue
        if link["node"]["type"] == "router":
            params = link["params"]
            if "dhcp_nameserver" not in params:
                continue
            dns_server_ip = params["dhcp_nameserver"]
            if "name" not in link["switch"]:
                continue
            sw_name = link["switch"]["name"]
            if sw_name not in switch_name_to_dns_ip:
                switch_name_to_dns_ip[sw_name] = []
            switch_name_to_dns_ip[sw_name].append(dns_server_ip)

    # Add the switches IPs to the docker nodes
    for link in topology["links"]:
        node = link["node"]
        if "type" not in node:
            continue
        if node["type"] == "docker":
            sw = link["switch"]["name"]
            if sw not in list(switch_name_to_dns_ip.keys()):
                continue
            dns_list = switch_name_to_dns_ip[sw]
            if "dns" not in node:
                node["dns"] = []
            for dns in dns_list:
                node["dns"].append(dns)
            # add a default dns server
            node["dns"].append("1.1.1.1")
            # Ensure unicity and ordering, from python 3.7+, because dict is ordered:
            node["dns"] = list(dict.fromkeys(node["dns"]))


def _simu_create_validate_resources_path(resources_path: str) -> None:
    if os.path.exists(resources_path) is not True:
        raise Exception(
            'The provided resources path does not exist: "{}"'.format(resources_path)
        )


# -------------------------------------------------------------------------- #
# API helpers
# -------------------------------------------------------------------------- #


###
# Simulation helpers
###


def create_simulation_from_topology(
    topology_file: str = None,
    topology_resources_paths: Optional[List[Path]] = None,
) -> int:
    """Create a new simulation model in database based on the provided topology, along with optional resource files.

    :return: The ID of the created simulation.
    :rtype: :class:`int`

    :param topology_file: The path to a topology file containing the nodes and network topology to create.
    :type topology_file: :class:`str`
    :param topology_resources_paths: The path to resources that will be pushed into compatible nodes.
    :type topology_resources_paths: :class:`str`, optional

    >>> from cr_api_client import core_api
    >>> core_api.reset()
    >>> core_api.create_simulation_from_topology("data/topologies/topology-1-client.yaml")
    1

    """

    if topology_resources_paths is None:
        topology_resources_paths = []

    # Create a new simulation model in database based on the provided topology file path."""
    if topology_file is None:
        raise Exception("An topology file is required")

    # Validate YAML configuration file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML configuration file
    yaml_content = _read_yaml_topology_file(topology_file)

    # Parse YAML configuration
    # We use ruamel.yaml because it keeps anchors and
    # aliases in memory. It is very convenient when the simulation
    # is stored/fetched (references are kept!)
    loader = YAML(typ="rt")
    topology_content = loader.load(yaml_content)

    if "name" not in topology_content:
        raise Exception(
            "There should be a 'name' element in the YAML configuration file"
        )
    name = topology_content["name"]

    if "nodes" not in topology_content:
        raise Exception(
            "There should be a 'nodes' structure in the YAML configuration file"
        )

    if "links" not in topology_content:
        raise Exception(
            "There should be a 'links' structure in the YAML configuration file"
        )

    required = ["switch", "node", "params"]
    for link in topology_content["links"]:
        for req in required:
            if req not in link:
                raise Exception(
                    f"There should be a '{req}' parameter for every item of 'links' in the YAML configuration file"
                )

    _simu_create_add_implicit_topo_parameters(topology_content)

    simulation_dict = {"name": name, "network": topology_content, "resources_paths": []}

    # Normalize the resources paths
    normalized_paths = []
    for resource in topology_resources_paths:
        resource = os.path.normpath(resource)
        # Removing trailing slashes because they are ignored by ZipFile
        if resource.endswith("/"):
            resource = resource[::-1]
        normalized_paths.append(resource)
    topology_resources_paths = normalized_paths

    # Add a default resources directory if it exists.
    # If the topology is "path/to/topo.yaml", the default resources directory is "path/to/resources".
    default_resources_path = os.path.join(os.path.dirname(topology_file), "resources")
    if os.path.exists(default_resources_path) and os.path.isdir(default_resources_path):
        if default_resources_path not in topology_resources_paths:
            topology_resources_paths.append(default_resources_path)

    # Verify that we do not have the same resources path in the list
    if len(set(topology_resources_paths)) != len(topology_resources_paths):
        raise Exception("Identical resources paths have been given")

    for resource in topology_resources_paths:
        # Validate resources path
        _simu_create_validate_resources_path(resource)
        # take the absolute path
        simulation_dict["resources_paths"].append(os.path.abspath(resource))

    id_simulation = add_simulation(simulation_dict)

    # Prepare disk resources
    _simulation_execute_operation("prepare", id_simulation, "PREPARING")

    # TODO: Check that the docker volumes that will be mounted by simu_run are present on the filesystem
    # for ...: _simu_create_validate_resources_exists()

    return id_simulation


def create_simulation_from_basebox(
    basebox_id: str, add_internet: bool = False, add_host: bool = False
) -> int:
    """Create a new simulation model in database based on the provided basebox id, with
    optional internet and/or host connectivity.

    """

    if basebox_id is None:
        raise Exception("A basebox ID is required")

    # Create an topology with the provided basebox ID
    try:
        basebox = fetch_basebox(basebox_id)
    except Exception:
        raise Exception(
            f"Cannot find basebox in database from basebox ID '{basebox_id}'"
        )

    role = basebox["role"]
    nb_proc = basebox["nb_proc"]
    memory_size = basebox["memory_size"]

    yaml_content = f"""---
name: "{basebox_id}"
nodes:

  - &switch
    type: switch
    name: "switch"

  - &client
    type: virtual_machine
    name: "client"
    basebox_id: "{basebox_id}"
    nb_proc: {nb_proc}
    memory_size: {memory_size}
    roles: ["{role}"]
"""

    if add_host:
        yaml_content += """
  - &host_machine
    type: host_machine
    name: "host_machine"
"""

    if add_internet:
        # add default route to gateway, a gateway and a switch to plug the gateway and the router
        yaml_content += """
  - &router
    type: router
    name: "router"
    routes:
      - "0.0.0.0/0 -> 192.168.23.2"

  - &switch_internet
    type: switch
    name: "switch_internet"

  - &physical_gateway
    type: physical_gateway
    name: "physical_gateway"
"""
    else:
        yaml_content += """
  - &router
    type: router
    name: "router"
"""

    yaml_content += """
links:

  - switch: *switch
    node: *router
    params:
      ip: "192.168.2.1/24"
      dhcp_nameserver: "8.8.8.8"

  - switch: *switch
    node: *client
    params:
      ip: "192.168.2.2/24"
"""

    if add_host:
        yaml_content += """
  - switch: *switch
    node: *host_machine
    params:
      ip: "192.168.2.3/24"
"""

    if add_internet:
        yaml_content += """
  - switch: *switch_internet
    node: *router
    params:
      ip: "192.168.23.1/24"

  - switch: *switch_internet
    node: *physical_gateway
    params:
      ip: "192.168.23.2/24"
"""

    loader = YAML(typ="rt")
    network_structure = loader.load(yaml_content)

    simulation_dict = {"name": str(basebox_id), "network": network_structure}

    id_simulation = add_simulation(simulation_dict)

    # Prepare disk resources
    _simulation_execute_operation("prepare", id_simulation, "PREPARING")

    return id_simulation


###
# Topology helpers
###


def topology_file_add_websites(
    topology_file: str, websites: List[str], switch_name: str
) -> str:
    """Add docker websites node to a given topology, and return the updated topology."""

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    topology_yaml = topology_add_websites(topology_yaml, websites, switch_name)

    return topology_yaml


def topology_file_add_dga(
    topology_file: str,
    algorithm: str,
    switch_name: str,
    number: int,
    resources_dir: str,
) -> (str, List[str]):
    """Add docker empty websites node with DGA to a given topology, and return the updated topology."""

    # Validate

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    (topology_yaml, domains) = topology_add_dga(
        topology_yaml, algorithm, switch_name, number, resources_dir
    )

    return topology_yaml, domains


def topology_file_add_dns_server(
    topology_file: str,
    switch_name: str,
    resources_dir: str,
) -> (str, str):
    """Add a DNS server to a YAML topology.
    Returns the updated topology and the content of the DNS configuration file."""

    # Validate

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    (topology_yaml, dns_conf_content) = topology_add_dns_server(
        topology_yaml, switch_name, resources_dir
    )

    return topology_yaml, dns_conf_content


###
# Basebox helpers
###


def _raise_error_msg(result: dict) -> None:
    """
    Raise an error message if a task (eg the basebox verification) failed
    :param result: the result of the task
    :return: None
    """
    error_msg = "No error message returned"
    if "result" in result:
        if "error_msg" in result["result"]:
            error_msg = result["result"]["error_msg"]
        raise Exception(error_msg)
    else:
        raise Exception(f"No 'result' key in result: {result}")


def __baseboxes_verification_wait_until_complete(
    task_id: str, log_suffix: str = None, timeout: int = 3600
) -> dict:
    """
    Wait until the verification task representing by its id is completed
    :param task_id: the task id
    :param log_suffix: what to insert into the log
    :param timeout: the timeout to stop the task
    :return: the result of the basebox verification
    """

    start_time = time.time()

    finished = False
    while not (finished or (time.time() - start_time) > timeout):
        time.sleep(2)
        current_time = time.time()
        elapsed = int(current_time - start_time)
        if log_suffix is not None:
            logger.info(
                f"   [+] Currently verifying {log_suffix} for {elapsed} seconds (timeout at {timeout} seconds)"
            )
        else:
            logger.info(
                f"   [+] Currently running the verification for {elapsed} seconds"
            )

        result = _post("/basebox/status_verify", data={"task_id": task_id})
        result.raise_for_status()
        result = result.json()

        if "status" in result:
            current_status = result["status"]

            if current_status == "ERROR":
                error_message = result["error_msg"]
                raise Exception(
                    f"Error during verification operation: '{error_message}'"
                )
            elif current_status == "FINISHED":
                finished = True

    if not finished:
        error_msg = f"[-] Unable to terminate operation before timeout of {timeout} seconds. Stopping operation."
        result = verify_basebox_stop(task_id)
        stopped = result["status"] == "STOPPED"
        if stopped:
            result["result"] = dict()
            result["result"]["error_msg"] = error_msg
            return result
        else:
            raise Exception("Unable to stop verification task")

    result = _post("/basebox/result_verify", data={"task_id": task_id})
    result.raise_for_status()
    result = result.json()

    success = result["status"] == "FINISHED" and result["result"]["success"] is True

    if not success:
        error_msg = result["result"]["error_msg"]
        logger.error(
            f"[-] The basebox verification was executed with error: {error_msg}"
        )

    return result


def __wait_for_the_operation_to_start(task_id: str) -> bool:
    """
    Wait for a task to start
    :param task_id: the task id
    :return: Is the task running
    """

    running = False
    timeout = 10
    start_time = time.time()
    while not (running or (time.time() - start_time) > timeout):
        result = _post("/basebox/status_verify", data={"task_id": task_id})
        result.raise_for_status()
        result = result.json()
        running = result["status"] == "RUNNING"
        time.sleep(1)

    if not running:
        logger.error(
            f"[-] Unable to start operation before timeout of {timeout} seconds"
        )

    return running


def __handle_wait(
    wait: bool, task_id: str, log_suffix: str, timeout: int = 3600
) -> bool:
    """

    :param wait: Wait for the operation to be completed in backend
    :param task_id: the task id
    :param log_suffix: the string to be inserted in the log
    :param timeout: the time limit before stopping the task
    :return: the result of the verification
    """
    success = True

    if wait:
        # Wait for the operation to be completed in backend

        result = __baseboxes_verification_wait_until_complete(
            task_id=task_id, log_suffix=log_suffix, timeout=timeout
        )

        finished = "status" in result and result["status"] == "FINISHED"
        success = finished

        if success:
            if "result" in result:
                return result

        if not success:
            _raise_error_msg(result)

    else:
        # wait for the operation to start
        running = __wait_for_the_operation_to_start(task_id)

        if not running:
            success = False

    return success


# -------------------------------------------------------------------------- #
# Core API
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """Return Core API version."""

    result = _get("/simulation/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Core API version")

    return result.json()


def reset() -> Any:
    """Reset the database (clean tables) and
    re-populate it with static info (baseboxes, roles...)
    """

    _reset_database()
    _reset_virtclient()


def add_simulation(simulation_dict: dict) -> int:
    """Create simulation and return a simulation ID."""

    # Get the paths if some have been provided
    resources_paths = simulation_dict.pop("resources_paths", [])

    data = json.dumps(simulation_dict)

    # Creation of a folder containing all the resources, this folder will then be zipped
    with TemporaryDirectory() as main_resources:

        # copy all resources in the main temporary folder
        for resource in resources_paths:
            if os.path.isdir(resource):
                shutil.copytree(
                    resource,
                    os.path.join(
                        main_resources, os.path.basename(os.path.normpath(resource))
                    ),
                )
            elif os.path.isfile(resource):
                shutil.copyfile(
                    resource,
                    os.path.join(
                        main_resources, os.path.basename(os.path.normpath(resource))
                    ),
                )
            else:
                raise Exception(f"Can not copy {resource}")

        # We have to create a new temporary folder to host the archive
        with TemporaryDirectory() as temp_dir:
            zip_file_name = _zip_resources(main_resources, temp_dir)
            resources_file = open(zip_file_name, "rb")
            files = {"resources_file": resources_file, "data": data}
            try:
                result = _post(
                    "/simulation/",
                    files=files,
                )
            finally:
                resources_file.close()

    if not main_resources:
        result = _post(
            "/simulation/",
            data=data,
            headers={"Content-Type": "application/json"},
        )

    if result.status_code != 200:
        _handle_error(result, "Cannot post simulation information to core API")

    id_simulation = result.json()["id"]
    return id_simulation


def simulation_status(id_simulation: int) -> str:
    """Return only the status of the simulation"""
    result = _get(f"/simulation/{id_simulation}/status")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    return result.json()


def fetch_simulation(id_simulation: int) -> dict:
    """Return a simulation dict given a simulation id."""
    result = _get(f"/simulation/{id_simulation}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    simulation_dict = result.json()

    return simulation_dict


def fetch_simulations() -> List[Any]:
    """Get the list of simulations, including the currently running simualtion, along with
    information on nodes

    """
    result = _get("/simulation/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    simulation_list = result.json()
    return simulation_list


def delete_simulation(id_simulation: int) -> Any:
    """Delete a simulation in database."""

    # Destroy simulation if it is running
    if simulation_status(id_simulation) == "RUNNING":
        _simulation_execute_operation("destroy", id_simulation, "STOPPING")

    _simulation_execute_operation("delete_snapshots", id_simulation, "STOPPING")

    # Delete simulation nodes
    delete_nodes(id_simulation)

    # Delete simulation
    result = _delete(f"/simulation/{id_simulation}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete simulation from core API")

    return result.json()


def update_simulation(id_simulation: int, simulation_dict: dict) -> Any:
    """Update simulation information information given a simulation id
    and a dict containing simulation info.
    """
    data = json.dumps(simulation_dict)
    result = _put(
        f"/simulation/{id_simulation}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update simulation information")

    return result.json()


def fetch_simulation_topology(id_simulation: int) -> Any:
    """Return the topology of a simulation."""
    result = _get(f"/simulation/{id_simulation}/topology")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation topology info")

    return result.json()


def fetch_simulation_topology_yaml(id_simulation: int) -> Any:
    """Return the YAML topology content of a simulation."""
    result = _get(f"/simulation/{id_simulation}/topology_yaml")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation topology info")

    return result.json()


def fetch_assets(id_simulation: int) -> Any:
    """Return the list of the assets
    of a given simulation. It corresponds to
    the list of the nodes with some additional
    information.
    """
    result = _get(f"/simulation/{id_simulation}/assets")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve assets from core API")

    return result.json()


def fetch_node(node_id: int) -> Any:
    """Return a node given its ID"""
    result = _get(f"/node/{node_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node from core API")

    return result.json()


def fetch_node_by_name(id_simulation: int, node_name: str) -> Any:
    """Return a node given its name"""

    result = _get(f"/simulation/{id_simulation}/node/{node_name}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation nodes from core API")

    return result.json()


def fetch_nodes_by_roles(id_simulation: int) -> Any:
    """Return a dict wkere keys are roles (such as 'ad', 'file_server', 'client', ...) and
    values are nodes.

    """
    result = _get(f"/simulation/{id_simulation}/nodes_by_roles")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve nodes")

    roles_dict = result.json()
    return roles_dict


def fetch_nodes_by_network_id(id_simulation: int, network_id: str) -> Any:
    """Return nodes list given a network id."""
    # Fetch node network interfaces
    result = _get(f"/simulation/{id_simulation}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve network interfaces")

    network_interfaces = result.json()

    nodes = []

    for network_interface in network_interfaces:
        if network_interface["network_id"] == network_id:
            nodes.append(fetch_node(network_interface["node_id"]))

    return nodes


def delete_node(id_node: int) -> Any:
    """Delete simulation node given its ID."""
    # Fetch virtual node network interfaces
    network_interfaces = fetch_node_network_interfaces(id_node)

    # Delete each network interfaces
    for network_interface in network_interfaces:
        delete_network_interface(network_interface["id"])

    # Delete node
    result = _delete(f"/node/{id_node}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete node")

    return result.json()


def fetch_nodes(id_simulation: int) -> Any:
    """Return simulation nodes dict given
    a simulation ID, where keys are node names.
    """
    result = _get(f"/simulation/{id_simulation}/node")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation nodes from core API")

    return result.json()


def fetch_virtual_machines(id_simulation: int) -> List[dict]:
    """Return simulation virtual machines dict given a simulation ID,
    where keys are virtual machine names.
    """
    results = fetch_nodes(id_simulation)

    vm_only = filter(lambda m: m["type"] == "virtual_machine", results)
    return list(vm_only)


def delete_nodes(id_simulation: int) -> str:
    """Delete simulation nodes given a simulation ID."""

    # Fetch simulation nodes
    result = _get(f"/simulation/{id_simulation}/node")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete simulation nodes")

    nodes_list = result.json()

    # Delete each node
    for node in nodes_list:
        delete_node(node["id"])

    result_json = "{}"
    return result_json


def update_node(node_id: int, node_dict: dict) -> Any:
    """Update node information given a node id and a dict containing
    node data.
    """
    data = json.dumps(node_dict)
    result = _put(
        f"/node/{node_id}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update node information with core API")

    return result.json()


def get_node_statistics_by_id(id_node: int) -> Any:
    """
    Return aggregated statistics from CPU, memory, block devices and network interfaces.
    Note: you can get the node IDs using the simu_status command (or the fetch_simulations() function).
    """
    result = _get(f"/node/{id_node}/stats")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node statistics")

    return result.json()


def node_memorydump(id_node: int) -> Any:
    """
    Return RAM dump of a node in a running simulation
    Note: you can get the node IDs using the simu_status command (or the fetch_simulations() function).
    """
    file_path_key = "file_path"
    file_size_key = "file_size"
    status_key = "status"

    result = _get(f"/node/{id_node}/memorydump")

    if (
        result.status_code != 200
        or status_key not in result.json()
        or result.json()[status_key] != "STARTED"
    ):
        _handle_error(result, "Cannot initiate node memory dump fom core API")

    logger.info("[+] Initialized memory dump of node '{}'...".format(id_node))

    # Wait for the operation to be completed in backend
    # Note : loop inspired from _simulation_execute_operation
    while True:
        # Sleep before next iteration
        time.sleep(2)

        # Fetch the current status of the memdump
        result = _get(f"/node/{id_node}/memorydump_status")

        if result.status_code != 200:
            _handle_error(result, "Cannot get status of node memory dump fom core API")

        result_json = result.json()
        if not (
            all(k in result_json for k in (file_path_key, file_size_key, status_key))
        ):
            raise Exception(
                f"Contents of memory dump status update is not in the expected format (attributes '{file_path_key}', '{file_size_key}' and '{status_key}' expected)"
            )

        # Log info on progression
        if result_json[status_key] == "PROGRESS":
            logger.info(
                "  [+] Currently performing memory dump of node '{}' (current dump file size is {})...".format(
                    id_node, naturalsize(result_json[file_size_key], binary=True)
                )
            )
        elif result_json[status_key] == "SUCCESS":
            break
        else:
            raise Exception(
                "Error during memory dump of node {} operation: '{}'".format(
                    id_node, result_json[status_key]
                )
            )

    logger.info(
        "[+] Node memory dump (raw dump with libvirt) obtained, and placed in file {} ({}) on the server.".format(
            result_json[file_path_key],
            naturalsize(result_json[file_size_key], binary=True),
        )
    )

    return result_json[file_path_key], result_json[file_size_key]


def fetch_node_network_interfaces(id_node: int) -> Any:
    """Return network interfaces list given a node ID."""
    result = _get(f"/node/{id_node}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node network interfaces")

    return result.json()


def fetch_simulation_network_interfaces(id_simulation: int) -> Any:
    """Return network interfaces list given a simulation ID."""
    result = _get(f"/simulation/{id_simulation}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation network interfaces")

    return result.json()


def fetch_network_interface_by_mac(id_simulation: int, mac_address: str) -> Any:
    """Return network interface list given a mac address."""
    # Fetch node network interfaces
    result = _get(f"/simulation/{id_simulation}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve network interfaces")

    network_interfaces = result.json()

    for network_interface in network_interfaces:
        if network_interface["mac_address"] == mac_address:
            return network_interface
    else:
        return None


def delete_network_interface(id_network_interface: int) -> Any:
    """Delete network interface given an id."""
    result = _delete(f"/network_interface/{id_network_interface}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node network interfaces from core API")

    return result.json()


def update_network_interface(
    id_network_interface: int, network_interface_dict: dict
) -> Any:
    """Update network interface information information given a network interface id and a
    dict containing network info.

    """
    data = json.dumps(network_interface_dict)
    result = _put(
        f"/network_interface/{id_network_interface}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update network interface information")

    return result.json()


def fetch_baseboxes() -> Any:
    """Return baseboxes list."""
    result = _get("/basebox")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve baseboxes list from core API")

    baseboxes = result.json()
    return baseboxes


def fetch_basebox(id_basebox: str) -> Any:
    """Return basebox given a basebox id."""
    result = _get(f"/basebox/id/{id_basebox}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    basebox = result.json()
    return basebox


def reload_baseboxes() -> Any:
    """
    Call the cyber range API to reload the list of available baseboxes.

    :return:
    """
    result = _get("/basebox/reload")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    return result.json()


def verify_basebox_result(task_id: str) -> Any:
    """
     Call the API to get the result the current verification.

    :param task_id: the task id
    :return: the result of the verification

    """

    data = {"task_id": task_id}

    try:
        result = _post(
            "/basebox/result_verify",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(result, "Cannot get verification result")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting verification result: '{}'".format(e))


def verify_basebox_stop(task_id: str) -> Any:
    """
    Call the API to stop the current verification
    :return:
    """
    data = {"task_id": task_id}

    result = _post("/basebox/stop_verify", data=data)

    if result.status_code != 200:
        _handle_error(result, "Cannot stop verification task")

    return result.json()


def verify_basebox_status(task_id: str) -> Any:
    """
    Call the API to get the status of current verification
    :return:
    """
    data = {"task_id": task_id}

    try:
        result = _post("/basebox/status_verify", data=data)

        if result.status_code != 200:
            _handle_error(result, "Cannot get verify status")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting verify status: '{}'".format(e))


def verify_basebox(id_basebox: int) -> Any:
    """
    Call the API to verify the checksum of the given basebox
    :param id_basebox: the id of the basebox to verify
    :return:
    """
    result = _get(f"/basebox/verify/{id_basebox}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    result = result.json()
    task_id = result["task_id"]
    success = result["result"] == "STARTED"

    if not success:
        _raise_error_msg(result)

    logger.info(f"[+] Verification task ID: {task_id}")

    result = __handle_wait(
        wait=True, task_id=task_id, log_suffix=id_basebox, timeout=3600
    )

    return {
        "success": result["result"]["success"],
        "task_id": task_id,
        "valid_checksum": result["result"]["valid_checksum"],
    }


def verify_baseboxes() -> Any:
    """
    Call the API to verify the checksum of all baseboxes
    :return:
    """
    result = _get("/basebox/verify/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    result = result.json()
    task_id = result["task_id"]
    success = result["result"] == "STARTED"

    if not success:
        _raise_error_msg(result)

    logger.info(f"[+] Verification task ID: {task_id}")

    result = __handle_wait(
        wait=True, task_id=task_id, log_suffix="all baseboxes", timeout=3600
    )

    return {
        "success": result["result"]["success"],
        "task_id": task_id,
        "result": result["result"]["valid_checksum"],
    }


def fetch_domains() -> Dict[str, str]:
    """Returns the mapping domain->IP"""

    # FIXME(multi-tenant): we should retrieve domains according to a simulation id
    result = _get("/network_interface/domains")

    if result.status_code != 200:
        _handle_error(result, "Error while fetching domains")

    return result.json()


def fetch_websites() -> Any:
    """Return websites list."""
    result = _get("/website")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve websites list from core API")

    websites = result.json()
    return websites


def topology_add_websites(
    topology_yaml: str, websites: List[str], switch_name: str
) -> str:
    """Add docker websites node to a given topology, and return the updated topology."""

    data_dict = {
        "topology_yaml": topology_yaml,
        "websites": websites,
        "switch_name": switch_name,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_websites",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding websites to a topology")

    topology_yaml = result.json()["topology_yaml"]

    return topology_yaml


def topology_add_dga(
    topology_yaml: str,
    algorithm: str,
    switch_name: str,
    number: int,
    resources_dir: str,
) -> Tuple[str, List[str]]:
    """Add docker empty websites with DGA node to a given topology, and return the updated topology
    associated with the domains."""

    data_dict = {
        "topology_yaml": topology_yaml,
        "algorithm": algorithm,
        "switch_name": switch_name,
        "number": number,
        "resources_dir": resources_dir,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_dga",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding websites to a topology")

    topology_yaml = result.json()["topology_yaml"]
    domains = result.json()["domains"]

    return topology_yaml, domains


def topology_add_dns_server(
    topology_yaml: str,
    switch_name: str,
    resources_dir: str,
) -> Tuple[str, str]:
    data_dict = {
        "topology_yaml": topology_yaml,
        "switch_name": switch_name,
        "resources_dir": resources_dir,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_dns_server",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding a DNS server to a topology")

    topology_yaml = result.json()["topology_yaml"]
    dns_conf = result.json()["dns_conf"]

    return topology_yaml, dns_conf


def tools_generate_domains(
    algorithm: str,
    number: int,
) -> List[str]:
    """
    Generate domain names according to the given algorithm
    :param algorithm: algorithm to use
    :param number: number of domains to generate
    :return: A list of domains
    """
    data_dict = {
        "algorithm": algorithm,
        "number": number,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/domain/generate_domains",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while generating domains")

    domains = result.json()["domains"]

    return domains


def fetch_topologies() -> Any:
    """Return topologies list."""
    result = _get("/topology")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve topologies list from core API")

    topologies = result.json()
    return topologies


###
# Simulation commands
###


def start_simulation(id_simulation: int, use_install_time: bool = False) -> None:
    """Start the simulation, with current time (by default) or time where the VM was created
    (use_install_time=True).

    """
    # Check that no other simulation is running
    simulation_list = fetch_simulations()
    for simulation in simulation_list:
        if simulation["status"] == "RUNNING":
            raise Exception(
                "Cannot start a new simulation, as the simulation '{}' is "
                "already running".format(simulation["id"])
            )

    # Initiate the simulation
    _simulation_execute_operation(
        "start", id_simulation, "STARTING", optional_param=use_install_time
    )


def pause_simulation(id_simulation: int) -> None:
    """Pause a simulation (calls libvirt suspend API)."""
    _simulation_execute_operation("pause", id_simulation, "PAUSING")


def unpause_simulation(id_simulation: int) -> None:
    """Unpause a simulation (calls libvirt resume API)."""
    _simulation_execute_operation("unpause", id_simulation, "UNPAUSING")


def halt_simulation(id_simulation: int) -> Optional[uuid.UUID]:
    """Properly stop a simulation, by sending a shutdown signal to the operating systems."""
    _simulation_execute_operation("stop", id_simulation, "STOPPING")


def destroy_simulation(id_simulation: int) -> None:
    """Stop a simulation through a hard reset."""
    _simulation_execute_operation("destroy", id_simulation, "STOPPING")


def clone_simulation(id_simulation: int) -> int:
    """Clone a simulation and create a new simulation, and return the new ID."""
    id_new_simulation = _simulation_execute_operation("clone", id_simulation, "CLONING")
    return id_new_simulation


def net_set_tap(id_simulation: int, simu_nodes: Dict = None) -> None:
    """Configure the network collections points.

    :param id_simulation: The id of the simulation.
    :param simu_nodes: A dictionary storing the collection points to capture.

    :type id_simulation: :class:`int`, ex : 1
    :type simu_nodes: :class:`Dict`, ex : {'switchs': [['switch1', 'client1']], 'nodes': ['client2']}

    """

    if simu_nodes["switchs"] is None and simu_nodes["nodes"] is None:
        for node in fetch_nodes(id_simulation):
            if node["type"] == "switch":
                update_node(node["id"], {"capture": True})
            else:
                for network_interface in node["network_interfaces"]:
                    update_network_interface(network_interface["id"], {"capture": True})
    else:
        if simu_nodes["switchs"] is not None:
            for switch_nodes in simu_nodes["switchs"]:
                switch = fetch_node_by_name(id_simulation, switch_nodes[0])
                update_node(switch["id"], {"capture": True})
                if switch_nodes[1:]:
                    for node_name in switch_nodes[1:]:
                        node = fetch_node_by_name(id_simulation, node_name)

                        network_interface_captured = False
                        for network_interface in node["network_interfaces"]:
                            if (
                                network_interface["network_id"] == switch["name"]
                                or network_interface["network_id"]
                                == switch["network_id"]
                            ):
                                update_network_interface(
                                    network_interface["id"], {"capture": True}
                                )
                                network_interface_captured = True

                        if not network_interface_captured:
                            raise Exception(
                                "The node '{}' isn't linked with the switch '{}'".format(
                                    node_name, switch["name"]
                                )
                            )
                else:
                    switch_network_id = (
                        switch["name"]
                        if switch["network_id"] is None
                        else switch["network_id"]
                    )
                    list_of_nodes = fetch_nodes_by_network_id(
                        id_simulation, switch_network_id
                    )
                    for node in list_of_nodes:
                        for network_interface in node["network_interfaces"]:
                            if network_interface["network_id"] == switch_network_id:
                                update_network_interface(
                                    network_interface["id"], {"capture": True}
                                )

        if simu_nodes["nodes"] is not None:
            for node_name in simu_nodes["nodes"]:
                for network_interface in fetch_node_by_name(id_simulation, node_name)[
                    "network_interfaces"
                ]:
                    update_network_interface(network_interface["id"], {"capture": True})


def net_unset_tap(id_simulation: int) -> None:
    """Reset the network collecting points configuration.

    :param id_simulation: The id of the simulation.

    :type id_simulation: :class:`int`, ex : 1

    """

    nodes = fetch_nodes(id_simulation)

    for node in nodes:
        if node["type"] == "switch":
            update_node(node["id"], {"capture": False})
        else:
            for network_interface in node["network_interfaces"]:
                update_network_interface(network_interface["id"], {"capture": False})


def net_start_capture(id_simulation: int, iface: str, pcap: bool, filter: str) -> None:
    """Redirect network traffic to the tap interface.

    :param id_simulation: The id of the simulation.
    :param iface: Interface where the traffic is mirrored to.
    :param pcap: A boolean indicating if the capture should be saved on disk in a pcap file (to be included in dataset)
    :param filter: 

    :type id_simulation: :class:`int`, ex : 1
    :type iface: :class:`str`, ex : dummy0
    :type pcap: :class:`bool` 
    :type filter: :class:`str` 

    """

    data_dict = {
        "iface": iface,
        "pcap": pcap,
        "filter": filter,
    }

    data = json.dumps(data_dict)
    result = _post(
        f"/simulation/{id_simulation}/tap",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(
            result, "Cannot activate network traffic redirection from core API"
        )


def net_stop_capture(id_simulation: int) -> None:
    """Stop redirection of network traffic to the tap interface.

    :param id_simulation: The id of the simulation.

    :type id_simulation: :class:`int`, ex : 1

    """
    result = _get(f"/simulation/{id_simulation}/untap")

    if result.status_code != 200:
        _handle_error(result, "Cannot stop network traffic redirection from core API")


def fetch_list_tap(id_simulation: int) -> None:
    """Return the list of collecting points used to capture the network traffic of a simulation.

    :param id_simulation: The id of the simulation.

    :type id_simulation: :class:`int`, ex : 1

    """

    list_tap = {"switchs": [], "nodes": []}

    # Get nodes to capture from simulation
    result = _get(f"/simulation/{id_simulation}/capture")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation nodes from core API")

    switchs_to_capture = result.json()["switchs"]

    nodes_to_capture = []
    for network_interface in result.json()["network_interfaces"]:
        node = fetch_node(network_interface["node_id"])
        if node not in nodes_to_capture:
            nodes_to_capture.append(node)

    # Return None if there is nothing to capture
    if switchs_to_capture == [] and nodes_to_capture == []:
        return None

    # Return {} if every node must be captured
    if len(switchs_to_capture) + len(nodes_to_capture) == len(
        fetch_nodes(id_simulation)
    ):
        return {}

    for node in nodes_to_capture:
        list_tap["nodes"].append(node["name"])

    for switch in switchs_to_capture:
        switch_dict = {"name": switch["name"], "nodes": []}

        # Getting nodes with the same network_id than the switch
        switch_network_id = (
            switch["name"] if switch["network_id"] is None else switch["network_id"]
        )
        list_of_nodes = fetch_nodes_by_network_id(id_simulation, switch_network_id)

        for node in list_of_nodes:
            if node in nodes_to_capture:

                # If every network_interface from a node is captured, it goes to the "nodes" dict
                capture_all_network_interfaces = True
                for network_interface in node["network_interfaces"]:
                    capture_all_network_interfaces = (
                        capture_all_network_interfaces and network_interface["capture"]
                    )

                # Else
                if capture_all_network_interfaces is False:
                    for network_interface in node["network_interfaces"]:
                        if (
                            network_interface["network_id"] == switch_network_id
                            and network_interface["capture"]
                        ):
                            switch_dict["nodes"].append(node["name"])
                            if node["name"] in list_tap["nodes"]:
                                list_tap["nodes"].remove(node["name"])
        if switch_dict["nodes"]:
            list_tap["switchs"].append(switch_dict)

    return list_tap


def fetch_pcaps(id_simulation: int) -> None:
    """Return the list of pcap files of a simulation.

    :param id_simulation: The id of the simulation.

    :type id_simulation: :class:`int`, ex : 1

    """

    result = _get(f"/simulation/{id_simulation}/pcaps")

    if result.status_code != 200:
        _handle_error(result, "Cannot fetch pcap files from core API")

    pcaps_list = result.json()

    return pcaps_list


def snapshot_simulation(id_simulation: int) -> str:
    """Create a snapshot of a simulation.

    All the files will be stored to
    /cyber-range-catalog/simulations/<hash campaign>/<timestamp>/

    This API call returns the path where the topology file will be stored.

    Parameters:

    id_simulation: int
        Simulation to snapshot

    """

    # simu_snap can only be done on a RUNNING simulation
    if simulation_status(id_simulation) != "RUNNING":
        raise Exception(
            "Cannot create a snapshot of the simulation, as the simulation '{}' is "
            "not running".format(id_simulation)
        )

    # Call snapshot API
    result = _post(f"/simulation/{id_simulation}/snapshot")
    if result.status_code != 200:
        _handle_error(result, "Error while creating snapshot")

    yaml: str = result.json()

    logger.info(f"[+] Starting the snapshot of simulation {id_simulation}...")
    while simulation_status(id_simulation) != "SNAPSHOT":
        time.sleep(1)

        simulation_dict = fetch_simulation(id_simulation)
        current_status = simulation_dict["status"]
        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation snapshot: '{}'".format(error_message)
            )

    logger.info("[+] Snapshot process has started")

    while simulation_status(id_simulation) != "READY":
        logger.info("  [+] Snapshot in progress...")
        time.sleep(1)

        simulation_dict = fetch_simulation(id_simulation)
        current_status = simulation_dict["status"]
        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation snapshot: '{}'".format(error_message)
            )

    return yaml


def virtclient_status() -> Any:
    """Get virtclient service status."""
    result = _get("/simulation/virtclient_status")

    if result.status_code != 200:
        _handle_error(result, "Cannot get virtclient service status")

    simulation_dict = result.json()
    return simulation_dict


def add_dns_entries(id_simulation: int, dns_entries: Dict[str, str]) -> str:
    """Add volatile DNS entries to the current simulation. Volatile means that it is not
    stored in database.

    """

    data = json.dumps(dns_entries)
    result = _post(
        f"/simulation/{id_simulation}/add_dns_entries",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding DNS entries")


def generate_malicious_domains(algorithm: str = None, number: int = 1) -> List[str]:
    """Generate and return a list of malicious domains."""

    data_dict = {
        "algorithm": algorithm,
        "number": number,
    }
    data = json.dumps(data_dict)

    result = _post(
        "/topology/generate_malicious_domains",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding DNS entries")

    domains = result.json()
    return domains["domains"]


def create_dataset(
    id_simulation: int, dont_check_logs_path: bool = False
) -> Optional[uuid.UUID]:
    """
    Handles the creation of the dataset after the end of a simulation

    Must be called after a STOP operation, and once all compute servers
    (virtclient) have fully stopped.

    Basically, this function communicates with the the core API, which itself
    communicates with the publish server's "backend" API.

    :param id_simulation: the simulation which was just stopped and from which output the dataset should be created
    :return: the new dataset id
    """

    logger.info(
        "[+] Going to create dataset based on data produced by simulation ID '{}'".format(
            id_simulation
        )
    )

    # Do a small check for the sake of helping the user and giving better
    # user experience: check if the rsyslog docker (which collects logs)
    # is inside the topology, and if so, check the "host_path" for logs
    # (a specific path is expected, and is hardcoded in Virtcleint's StopSimulationCmd)
    if dont_check_logs_path is False:
        topology = YAML().load(fetch_simulation_topology_yaml(id_simulation))

        # The path of the logs, on the compute server file system should ALWAYS be as follows
        rsyslog_docker_present: bool = False
        potential_logs_rel_path: List[Path] = []
        for node in topology["nodes"]:
            if (
                node["type"] == "docker"
                and "rsyslog" in node["base_image"]
                and "volumes" in node
            ):
                rsyslog_docker_present = True
                for volume in node["volumes"]:
                    if (
                        "host_path" in volume
                        and "writable" in volume
                        and volume["writable"]
                    ):
                        potential_logs_rel_path.append(Path(volume["host_path"]))

        # If no rsyslog docker is present, jsut issue a non-blocking warning
        if not rsyslog_docker_present:
            logger.warning(
                "  [+] The collection of logs was not activated for the simulation (the rsyslog docker is not present in the topology). No log will be included in the dataset."
            )
        else:
            wrong_host_path = True
            for p in potential_logs_rel_path:
                if p.is_absolute():
                    p = Path(str(p)[1:])
                if p == Path("shared_resources/rsyslog/logs"):
                    wrong_host_path = False
                    break

            if wrong_host_path:
                logger.error(
                    "  [+] It seems that the simulation includes the 'rsyslog' docker that collects the logs, but does not specify the appropriate host_path for the logs. It is expected that the rsyslog docker node specifies a (writable) volume with a host_path equal to '/shared_resources/rsyslog/logs'. Candidates are '{}' instead.".format(
                        [str(p) for p in potential_logs_rel_path],
                    )
                )
                logger.error(
                    " [+] Dataset creation aborted. You may wish to move the log files to the appropriate folder on the compute server(s), and then retry. Alternatively, you can bypass this check with the dont_check_log_path option."
                )
                return None

    # Ask the core API to contact the /backend/ publish server API
    # in order to start the dataset creation process
    result = _post(f"/create_dataset/{id_simulation}")
    if result.status_code != 200:
        _handle_error(result, "Cannot initiate the creation of the dataset")

    dataset_id = result.json()["dataset_id"]

    logger.info(f"  [+] Dataset pre-created with dataset id {dataset_id}")

    # Start an active waiting loop until the dataset creation if fully complete
    # Indeed, dataset creation involves the download of potentially large
    # files overs the network, which can take some time!
    max_retries = 5
    retries = max_retries
    while True:
        time.sleep(2)

        result = _get(f"/create_dataset/status/{dataset_id}")
        if result.status_code != 200:
            if (
                result.headers.get("content-type") == "application/json"
                and "message" in result.json()
            ):
                error_msg = result.json()["message"]
            else:
                error_msg = result.text

            # Retry to get the status a couple of times before qsending back an error
            if retries == 0:
                raise Exception(
                    "Error during creation of dataset {}: could not get status of the dataset creation after {} tries. Core API HTTP status: {}. Response: {} ".format(
                        dataset_id, max_retries, result.status_code, error_msg
                    )
                )
            else:
                logger.warning(
                    "  [+] Could not get status of dataset creation (Retries left: {}. Core API HTTP status: {}. Response: {})".format(
                        retries, result.status_code, error_msg
                    )
                )
                retries -= 1
        else:
            # Reset the number of retries
            retries = max_retries

            # Get the status and message
            dataset_creation_status = result.json()["status"]
            dataset_creation_message = result.json()["message"]

            logger.info(
                "  [+] Dataset creation in progress (Status: {}{})".format(
                    dataset_creation_status,
                    f". Message is {dataset_creation_message}."
                    if dataset_creation_message
                    else "",
                )
            )

            if dataset_creation_status == "FINISHED":
                # All went well
                break
            elif dataset_creation_status == "FINISHED_ERROR":
                # The dataset creation encountered errors
                raise Exception(
                    "Error during creation of dataset {}: dataset creation ended with errors ('{}').".format(
                        dataset_id, dataset_creation_message
                    )
                )
            # Otherwise, dataset creation is not finished, just loop

    logger.info("[+] Dataset creation was correctly executed")

    # Set the simulation status to READY
    update_simulation(id_simulation, {"status": "READY"})

    simulation = fetch_simulation(id_simulation)
    logger.info("[+] Current simulation status: '{}'".format(simulation["status"]))

    return uuid.UUID(dataset_id)


def stop_dataset_creation(dataset_id: uuid.UUID) -> Any:
    """
    Stops/aborts the creation of a dataset that is in the process of being created.

    This function should be used, for instance, if a dataset creation has been
    automatically started although the user does not want a dataset, and the dataset
    creation process is taking too much time.

    WARNING: after stopping the dataset creation, it is advised to delete or at least
    repair the dataset.

    :param dataset_id: the dataset which is in the process of being created and that must be aborted
    :return: return the json body of the core API response
    """
    # Simply calls the core API which itself asks the publish
    # server (backend) to stop of the dataset creation process.

    result = _put("/create_dataset/stop/{}".format(str(dataset_id)))

    if result.status_code != 200:
        _handle_error(result, "Cannot stop dataset creation through core API")

    return result.json()
