# standard imports
import hashlib
import importlib
import json
import logging
import os
import sys
import tempfile
from typing import Callable, TypedDict, Union

import requests
from cic.contract.constants import CONTRACT_URLS

# local imports
from cic.writers import WritersType


log = logging.getLogger(__name__)


# Download File from Url
def download_file(url: str, filename=None) -> str:
    directory = tempfile.gettempdir()
    filename = filename if filename else url.split("/")[-1]
    log.debug(f"Downloading {filename}")
    r = requests.get(url, allow_redirects=True)
    content_hash = hashlib.md5(r.content).hexdigest()
    path = os.path.join(directory, content_hash)
    with open(path, "wb") as f:
        f.write(r.content)
    log.debug(f"{filename} downloaded to {path}")
    return path


def get_contract_args(data: list):
    for item in data:
        if item["type"] == "constructor":
            return item["inputs"]
    raise Exception("No constructor found in contract")


def select_contract():
    print("Contracts:")
    print("\t C - Custom (path/url to contract)")
    for idx, contract in enumerate(CONTRACT_URLS):
        print(f"\t {idx} - {contract['name']}")

    val = input("Select contract (C,0,1..): ")
    if val.isdigit() and int(val) < len(CONTRACT_URLS):
        contract = CONTRACT_URLS[int(val)]
        bin_path = os.path.abspath(download_file(contract["url"] + ".bin"))
        json_path = download_file(contract["url"] + ".json")

    elif val == "C":
        possible_bin_location = input("Enter a path or url to a contract.bin: ")
        if possible_bin_location.startswith("http"):
            # possible_bin_location is url
            bin_path = download_file(possible_bin_location)
        else:
            # possible_bin_location is path
            if os.path.exists(possible_bin_location):
                bin_path = os.path.abspath(possible_bin_location)
            else:
                raise Exception(f"File {possible_bin_location} does not exist")

            possible_json_path = val.replace(".bin", ".json")
            if os.path.exists(possible_json_path):
                json_path = possible_json_path
    else:
        print("Invalid selection")
        sys.exit(1)
    contract_extra_args = []
    contract_extra_args_types = []

    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            json_data = json.load(f)
        for contract_arg in get_contract_args(json_data):
            arg_name = contract_arg.get("name")
            arg_type = contract_arg.get("type")
            if arg_name not in ["_decimals", "_name", "_symbol"]:
                val = input(f"Enter value for {arg_name} ({arg_type}): ")
                contract_extra_args.append(val)
                if arg_type == "uint128":
                    contract_extra_args_types.append("uint256")
                else:
                    contract_extra_args_types.append(arg_type)

    return {
        "bin_path": bin_path,
        "json_path": json_path,
        "extra_args": contract_extra_args,
        "extra_args_types": contract_extra_args_types,
    }


class Writers(TypedDict):
    meta: Union[WritersType, Callable[..., WritersType]]
    attachment: Callable[..., WritersType]
    proof: Callable[..., WritersType]
    ext: Union[WritersType, Callable[..., WritersType]]


def init_writers_from_config(config) -> Writers:
    writers = {}
    writer_keys = ["meta", "attachment", "proof", "ext"]
    for key in writer_keys:
        writer_config_name = f"CIC_CORE_{key.upper()}_WRITER"
        (module_name, attribute_name) = config.get(writer_config_name).rsplit(
            ".", maxsplit=1
        )
        mod = importlib.import_module(module_name)
        writer = getattr(mod, attribute_name)
        writers[key] = writer

    return Writers(
        meta=writers["meta"],
        attachment=writers["attachment"],
        proof=writers["proof"],
        ext=writers["ext"],
    )
