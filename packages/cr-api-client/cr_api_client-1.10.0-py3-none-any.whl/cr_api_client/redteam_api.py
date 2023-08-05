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
import time
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import requests
from colorama import Fore
from loguru import logger

# Configuration access to Cyber Range endpoint
REDTEAM_API_URL = "http://127.0.0.1:5004"
# Expect a path to CA certs (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CA_CERT_PATH = None
# Expect a path to client cert (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_CERT_PATH = None
# Expect a path to client private key (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_KEY_PATH = None

# Module variables
attack_list = {}


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: str) -> requests.Response:
    return requests.get(
        f"{REDTEAM_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _post(route: str, **kwargs: str) -> requests.Response:
    return requests.post(
        f"{REDTEAM_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _put(route: str, **kwargs: str) -> requests.Response:
    return requests.put(
        f"{REDTEAM_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _delete(route: str, **kwargs: str) -> requests.Response:
    return requests.delete(
        f"{REDTEAM_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _handle_error(result: requests.Response, context_error_msg: str) -> None:
    if result.headers.get("content-type") == "application/json":
        error_msg = str(result.json())  # ["message"]
    else:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


# -------------------------------------------------------------------------- #
# Redteam API
# -------------------------------------------------------------------------- #

def get_version() -> str:
    """Return Redteam API version."""
    result = _get("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Redteam API version")

    return result.json()

def reset_redteam() -> None:
    """Reset redteam platform (init knowledge_database and delete all workers).

    :return: None

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()

    """
    result = _delete("/platform")
    result.raise_for_status()


def list_attacks(status: str = None) -> List[dict]:
    """List all attacks available and done.

    :param status: The status (success, failed, error, running, runnable) to filter.
    :type status: :class:`str`

    :return: List all attacks in JSON format.
    :rtype: :class:`List`

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()
    >>> redteam_api.list_attacks(status="success")
    []

    """
    url = "/attack"

    if status:
        url = url + "?status=" + status
    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available attacks from redteam API")

    return result.json()


def attack_infos(id_attack: str) -> Tuple[str, List[dict]]:
    """Return status and output for attack.

    :param id_attack: The attack identifier.
    :type id_attack: :class:`int`

    :return: Status of attack and output data.
    :rtype: :class:`str`, :class:`Dict`

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()
    >>> redteam_api.attack_infos(id_attack=1)
    ('runnable', None)

    """
    url = "/attack/" + str(id_attack)

    result = _get(url, headers={}, data={})
    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve attack from redteam API")
    res_json = result.json()
    output = None
    if res_json["output"]:
        output = json.loads(res_json["output"])
    return res_json["status"], output


def __waiting_attack(id_attack: str, name: str, waiting_worker: bool = True) -> str:
    """
    Waiting for attack status (waiting, success or failed).

    :param id_attack: The attack identifier.
    :type id_attack: :class:`int`
    :param attack_name: The worker name for this attack.
    :type attack_name: :class:`str`
    :param waiting_worker: Wait attack status become "success" or "failed".
    :type waiting_worker: :class:`bool`, optional

    :return: The ID of attack.
    :rtype: :class:`str`

    """
    url = "/attack/" + str(id_attack)

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve attack information from redteam API")

    status = result.json().get("status", None)
    cpt_max = 150
    cpt = 0
    while status not in ["success", "failed", "error"]:  # not finished
        time.sleep(1)
        cpt = cpt + 1
        result = _get(url, headers={}, data={})

        if result.status_code != 200:
            _handle_error(result, "Cannot retrieve attack information from redteam API")

        status = result.json().get("status", None)
        if status == "waiting":
            logger.info(f"[+] ({id_attack}) Attack {name} is waiting.")
            if not waiting_worker:
                return id_attack
        if cpt == cpt_max:
            status = "error"
            _handle_error(result, f"Attack {name} error : TIMEOUT")
        time.sleep(1)

    if status == "success":
        color = Fore.GREEN
    elif status == "failed":
        color = Fore.YELLOW
    elif status == "error":
        color = Fore.RED
        _handle_error(result, f"Attack {name} error.")

    logger.info(
        f"[+] {Fore.BLUE}({id_attack}) Attack {name}{Fore.RESET} : {color}{status}{Fore.RESET}"
    )
    return id_attack


def execute_attack(
    id_attack: int, name: str, waiting_worker: bool = True
) -> Optional[str]:
    """
    Start attack by id_attack.

    :param id_attack: The attack identifier.
    :type id_attack: :class:`int`
    :param attack_name: The worker name for this attack.
    :type attack_name: :class:`str`
    :param waiting_worker: Wait attack status become "success" or "failed".
    :type waiting_worker: :class:`bool`, optional

    :return: The ID of attack.
    :rtype: :class:`str`

    """
    url = "/attack/" + str(id_attack) + "?action=start"
    payload = {}
    headers = {}
    result = _get(url, headers=headers, data=payload)

    if result.status_code != 200:
        _handle_error(result, "Cannot start attack from redteam API")

    result = result.json()
    idAttack = result.get("idAttack", None)
    logger.info(f"[+] {Fore.BLUE}({idAttack}) Attack {name}{Fore.RESET} : started")
    logger.info(f"[+]     Values : {Fore.YELLOW}{result['values']}{Fore.RESET}")
    if idAttack is not None:
        return __waiting_attack(idAttack, name, waiting_worker)


def execute_attack_name(attack_name: str, waiting_worker: bool = True) -> Optional[str]:
    """
    Select attack by worker name (first occurence) and execute it.

    :param attack_name: The worker name for this attack.
    :type attack_name: :class:`str`
    :param waiting_worker: Wait attack status become "success" or "failed".
    :type waiting_worker: :class:`bool`, optional

    :return: The ID of attack.
    :rtype: :class:`str`

    """
    url = "/attack"
    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available attacks from redteam API")

    attack = next(
        (x for x in result.json() if x["worker"]["name"] == attack_name), None
    )

    if attack:
        return execute_attack(attack["idAttack"], attack_name, waiting_worker)
    else:
        logger.warning(f"[-] Attack {attack_name} not avalaible")


def __execute_attack_with_value(
    attack_name: str, waiting_worker: bool = True, values: Optional[Dict] = None
) -> Optional[str]:
    url = "/attack"
    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available attacks from redteam API")

    for attack in result.json():
        if attack["worker"]["name"] == attack_name:
            if values is not None:
                v_dict = json.loads(attack["values"])
                if set(values.items()).issubset(v_dict.items()):
                    target_attack = attack
                    break
            else:
                target_attack = attack
                break

    if target_attack:
        return execute_attack(
            id_attack=target_attack["idAttack"],
            name=attack_name,
            waiting_worker=waiting_worker,
        )
    else:
        logger.warning(f"[-] {Fore.RED} Attack {attack_name} not found.{Fore.RESET}")


def init_knowledge(data: List[dict]) -> bool:
    """
    Insert data in knowledge database.

    :return: boolean

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()
    >>> redteam_api.init_knowledge([{"host": {"host_ip": "x.x.x.x", "host": {"netbios_name": "WIN"}, "roles": []}}])
    True

    """
    output = {}

    for elt in data:
        key = list(elt)[0]
        output[key] = elt[key]

    url = "/knowledge"
    headers = {"Content-type": "application/json"}
    result = _post(url, headers=headers, data=json.dumps(output), timeout=10)

    if result.status_code != 200:
        _handle_error(result, "Cannot initialize knowledge database from redteam API")
    else:
        return True


def scenario_result() -> str:
    """
    Generate json report about all attack actions.

    :return: List all attacks done and runnning.

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()
    >>> redteam_api.scenario_result()
    []

    """

    url = "/report"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot get scenario result from redteam API")

    return result.json()


def attack_knowledge() -> str:
    """
    Get the attack knowledge (attack hosts and sessions).

    :return: Attack hosts and sessins.

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()
    >>> redteam_api.attack_knowledge()
    {'hosts': [], 'attack_sessions': []}

    """

    url = "/attack_knowledge"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot get attack knowledge result from redteam API")

    return result.json()
