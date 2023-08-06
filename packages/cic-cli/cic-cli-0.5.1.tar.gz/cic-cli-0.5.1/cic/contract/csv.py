import csv
import importlib
import logging
import os
from enum import IntEnum
from pathlib import Path
from typing import List

from chainlib.chain import ChainSpec
from cic.contract.components.attachment import Attachment
from cic.contract.components.meta import Meta
from cic.contract.components.proof import Proof
from cic.contract.components.token import Token
from cic.contract.constants import DMR_CONTRACT_URL, GITABLE_CONTRACT_URL
from cic.contract.contract import Contract
from cic.contract.helpers import download_file
from cic.contract.network import Network

log = logging.getLogger(__name__)

CONTRACT_CSV_HEADER = [
    "issuer",
    "namespace",
    "voucher_name",
    "symbol",
    "location",
    "country_code",
    "supply",
    "precision",
    "token_type",
    "demurrage",
    "period_minutes",
    "phone_number",
    "email_address",
    "sink_account",
    "description",
]


class CSV_Column(IntEnum):
    issuer = 0
    namespace = 1
    voucher_name = 2
    symbol = 3
    location = 4
    country_code = 5
    supply = 6
    precision = 7
    token_type = 8
    demurrage = 9
    period_minutes = 10
    phone_number = 11
    email_address = 12
    sink_account = 13
    description = 14


def load_contracts_from_csv(config, directory, csv_path: str) -> List[Contract]:
    targets = ["eth"]
    os.makedirs(directory)
    contract_rows = []
    with open(csv_path, "rt", encoding="utf-8") as file:
        csvreader = csv.reader(file, delimiter=",")
        for idx, row in enumerate(csvreader):
            if idx == 0:
                if row != CONTRACT_CSV_HEADER:
                    raise Exception(
                        f'Seems you are using the wrong csv format. Expected the header to be: \n\t {", ".join(CONTRACT_CSV_HEADER)}'
                    )
                continue
            contract_rows.append(row)
    contracts = []
    for idx, contract_row in enumerate(contract_rows):
        issuer = contract_row[CSV_Column.issuer]
        namespace = contract_row[CSV_Column.namespace]
        voucher_name = contract_row[CSV_Column.voucher_name]
        symbol = contract_row[CSV_Column.symbol]
        location = contract_row[CSV_Column.location]
        country_code = contract_row[CSV_Column.country_code]
        supply = contract_row[CSV_Column.supply]
        precision = contract_row[CSV_Column.precision]
        token_type = contract_row[CSV_Column.token_type]
        demurrage = contract_row[CSV_Column.demurrage]
        period_minutes = contract_row[CSV_Column.period_minutes]
        phone_number = contract_row[CSV_Column.phone_number]
        email_address = contract_row[CSV_Column.email_address]
        sink_account = contract_row[CSV_Column.sink_account]
        description = contract_row[CSV_Column.description]

        if token_type == "demurrage":
            bin_path = os.path.abspath(download_file(DMR_CONTRACT_URL + ".bin"))
            log.info(f"Generating {token_type} contract for {issuer}")
            token = Token(
                directory,
                name=voucher_name,
                symbol=symbol,
                precision=precision,
                supply=supply,
                extra_args=[demurrage, period_minutes, sink_account],
                extra_args_types=["uint256", "uint256", "address"],
                code=bin_path,
            )
        elif token_type == "giftable":
            bin_path = os.path.abspath(download_file(GITABLE_CONTRACT_URL + ".bin"))
            token = Token(
                directory,
                name=voucher_name,
                symbol=symbol,
                precision=precision,
                supply=supply,
                extra_args=[],
                extra_args_types=[],
                code=bin_path,
            )
        else:
            raise Exception(
                f"Only demurrage and gitable contracts currently supported at this time. {token_type} is not supported"
            )
        if token is None:
            raise Exception(f"There was an issue building the contract")

        token.start()

        log.info("Generating proof")
        proof = Proof(
            directory,
            attachments=None,
            issuer=issuer,
            description=description,
            namespace=namespace,
        )
        proof.start()

        log.info("Generating meta")
        meta = Meta(
            directory,
            name=issuer,
            contact={
                "phone": phone_number,
                "email": email_address,
            },
            country_code=country_code,
            location=location,
        )

        meta.start()

        log.info("Generating attachment")
        attachment = Attachment(directory)

        log.info("Generating network")
        network = Network(directory, targets=targets)
        network.start()

        log.info(
            f"""Populating infomation from network:
        CIC_REGISTRY_ADDRESS: {config.get("CIC_REGISTRY_ADDRESS")}
        CHAIN_SPEC: {config.get("CHAIN_SPEC")}
        RPC_PROVIDER: {config.get("RPC_PROVIDER")}
        """
        )
        for target in targets:
            # TODO Clean this up
            modname = f"cic.ext.{target}"
            cmd_mod = importlib.import_module(modname)
            signer_hint = config.get("WALLET_KEY_FILE")
            if signer_hint is None:
                raise Exception("No Wallet Keyfile was provided")
            keys = cmd_mod.list_keys(config, signer_hint)
            if keys is None or len(keys) == 0:
                raise Exception(f"No wallet keys found in {signer_hint}")
            if len(keys) > 1:
                log.warning(
                    f"More than one key found in the keystore. Using the first one\n - {keys[0]}"
                )
            key_account_address = keys[0]

            m = importlib.import_module(f"cic.ext.{target}.start")
            m.extension_start(
                network,
                registry_address=config.get("CIC_REGISTRY_ADDRESS"),
                chain_spec=ChainSpec.from_chain_str(config.get("CHAIN_SPEC")),
                rpc_provider=config.get("RPC_PROVIDER"),
                key_account_address=key_account_address,
            )
        network.load()

        contracts.append(
            Contract(
                token=token,
                proof=proof,
                meta=meta,
                attachment=attachment,
                network=network,
            )
        )
    return contracts


def load_contract_from_csv(config, directory, csv_path: str) -> Contract:
    path = Path(csv_path)
    if path.is_file():
        contracts = load_contracts_from_csv(config, directory, csv_path=csv_path)
        if len(contracts) == 0:
            raise Exception("No contracts found in CSV")
        if len(contracts) > 1:
            log.warning(
                "Warning multiple contracts found in CSV. Only the first contract will be used"
            )
    else:
        raise Exception("CSV file does not exist")
    return contracts[0]
