# Standard
import importlib
import logging
import os
from typing import List

# External imports
from chainlib.chain import ChainSpec
from chainlib.cli.config import Config

# Local Modules
from cic.contract.components.attachment import Attachment
from cic.contract.components.meta import Meta
from cic.contract.components.proof import Proof
from cic.contract.components.token import Token
from cic.contract.helpers import init_writers_from_config
from cic.contract.network import Network
from cic.contract.processor import ContractProcessor
from cic.writers import HTTPWriter, KeyedWriterFactory, MetadataWriter
from cic_types.ext.metadata import MetadataRequestsHandler
from cic_types.ext.metadata.signer import Signer as MetadataSigner

log = logging.getLogger(__name__)


class Contract:
    """ """

    def __init__(
        self,
        token: Token,
        proof: Proof,
        meta: Meta,
        attachment: Attachment,
        network: Network,
    ):
        self.token = token
        self.proof = proof
        self.meta = meta
        self.attachment = attachment
        self.network = network

    def __str__(self):
        s = ""
        s += f"\n[cic.header]\nversion = {self.proof.version()}\n\n"
        s += f"[cic.token]\n{self.token}\n"
        s += f"[cic.proof]\n{self.proof}\n"
        s += f"[cic.meta]\n{self.meta}\n"
        s += f"[cic.attachment]\n{self.attachment}\n"
        s += f"[cic.network]\n{self.network}\n"
        return s


def load_contract(directory) -> Contract:
    token = Token(path=directory)
    proof = Proof(path=directory)
    meta = Meta(path=directory)
    attachment = Attachment(path=directory)
    network = Network(directory)

    token.load()
    proof.load()
    meta.load()
    attachment.load()
    network.load()
    return Contract(
        token=token, proof=proof, meta=meta, attachment=attachment, network=network
    )


def generate_contract(
    directory: str, targets: List[str], config, interactive=True
) -> Contract:
    os.makedirs(directory)
    log.info("Generating token")
    token = Token(directory, interactive=interactive)
    token.start()

    log.info("Generating proof")
    proof = Proof(directory, interactive=interactive)
    proof.start()

    log.info("Generating meta")
    meta = Meta(directory, interactive=interactive)
    meta.start()

    log.info("Generating attachment")
    attachment = Attachment(directory, interactive=interactive)

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
        keys = cmd_mod.list_keys(config, signer_hint)
        if len(keys) > 1:
            print("More than one key found, please select one:")
            for idx, key in enumerate(keys):
                print(f"{idx} - {key} ")
            selecting_key = True
            while selecting_key:
                idx = int(input("Select key: "))
                if keys[idx] is not None:
                    key_account_address = keys[idx]
                    selecting_key = False
                else:
                    print("Invalid key, try again")
        else:
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

    return Contract(
        token=token, proof=proof, meta=meta, attachment=attachment, network=network
    )


def deploy_contract(
    config: Config,
    target: str,
    contract_directory: str,
):
    modname = f"cic.ext.{target}"
    cmd_mod = importlib.import_module(modname)

    writers = init_writers_from_config(config)
    output_directory = os.path.join(contract_directory, "out")
    output_writer_path_meta = output_directory

    metadata_endpoint = config.get("META_URL")
    metadata_auth_token = config.get("META_AUTH_TOKEN")
    headers = {"Authorization": f"Basic {metadata_auth_token}"}
    if metadata_endpoint is not None:
        MetadataRequestsHandler.base_url = metadata_endpoint
        MetadataRequestsHandler.auth_token = metadata_auth_token

        MetadataSigner.gpg_path = "/tmp"
        MetadataSigner.key_file_path = config.get("AUTH_KEYFILE_PATH")
        MetadataSigner.gpg_passphrase = config.get("AUTH_PASSPHRASE")
        writers["proof"] = KeyedWriterFactory(MetadataWriter, HTTPWriter).new
        writers["attachment"] = KeyedWriterFactory(None, HTTPWriter).new
        writers["meta"] = MetadataWriter
        output_writer_path_meta = metadata_endpoint

    ct = Token(path=contract_directory)
    cm = Meta(
        path=contract_directory, writer=writers["meta"](path=output_writer_path_meta)
    )
    ca = Attachment(
        path=contract_directory,
        writer=writers["attachment"](path=output_writer_path_meta, headers=headers),
    )
    cp = Proof(
        path=contract_directory,
        attachments=ca,
        writer=writers["proof"](path=output_writer_path_meta, headers=headers),
    )
    cn = Network(path=contract_directory)

    ca.load()
    ct.load()
    cp.load()
    cm.load()
    cn.load()

    chain_spec = None
    try:
        chain_spec = config.get("CHAIN_SPEC")
        log.debug(f"using CHAIN_SPEC from config: {chain_spec}")
    except KeyError:
        chain_spec = cn.chain_spec
        config.add(chain_spec, "CHAIN_SPEC", exists_ok=True)
        log.debug(f"using CHAIN_SPEC: {str(chain_spec)} from network")

    signer_hint = config.get("WALLET_KEY_FILE")
    (rpc, signer) = cmd_mod.parse_adapter(config, signer_hint)

    target_network_reference = cn.resource(target)
    chain_spec = cn.chain_spec(target)
    log.debug(
        f'found reference {target_network_reference["contents"]} chain spec {chain_spec} for target {target}'
    )
    c = getattr(cmd_mod, "new")(
        chain_spec,
        target_network_reference["contents"],
        cp,
        signer_hint=signer,
        rpc=rpc,
        outputs_writer=writers["ext"](path=output_directory),
    )
    c.apply_token(ct)

    p = ContractProcessor(proof=cp, attachment=ca, metadata=cm, extensions=[c])
    p.process()
