# CIC Token Deployment Tool
[![Status](https://ci.grassecon.net/api/badges/cicnet/cic-cli/status.svg)](https://ci.grassecon.net/grassrootseconomics/cic)
[![Version](https://img.shields.io/pypi/v/cic-cli?color=green)](https://pypi.org/project/cic/)

CIC-CLI provides tooling to generate and publish metadata in relation to
token deployments.

```shell
pip install cic-cli[eth]
```
## Usage
### Using the wizard  
First make sure that you edit the configs below to add your paths for `[auth]keyfile_path` and `[wallet]keyfile`
The configs are located in `~/.config/cic/cli/config/`
```
# Local
cic wizard ./somewhere -c ~/.config/cic/cli/config/docker

# Test Net
cic wizard ./somewhere -c ~/.config/cic/cli/config/testnet
```
### Modular
Some of the concepts described below assume familiarity with base
concepts of the CIC architecture. Please refer to the appropriate
documentation for more information.

To initialize a new token deployment for the EVM:

```shell
cic init --target eth --name <token_name> --symbol <token_symbol> --precision <token_value_precision> <settings_folder>
```

To automatically fill in settings detected in the network for the EVM:

```shell
cic ext --registry <contract_registry_address> -d <settings_folder> -i <chain_spec> -p <rpc_endpoint> eth
```


## Structure of the components

![image](./doc/sphinx/components.svg)

CIC-CLI is designed to interface any network type backend. The current
state of the package contains interface to EVM only. Thus, the examples
below are limited to the context of the EVM.

## Development
### Requirements
 - Install [poetry](https://python-poetry.org/docs/#installation) 

### Setup

```
 poetry install -E eth
```

### Running the CLI

```bash
 poetry run cic -h
```

```bash
 poetry run cic wizard ./somewhere -c ./config/docker
```
### Importing a wallet from metamask
- Export the accounts private key [Instructions](https://metamask.zendesk.com/hc/en-us/articles/360015289632-How-to-Export-an-Account-Private-Key)
- Save the private key to a file
- Run `eth-keyfile -k <file> > ~/.config/cic/keystore/keyfile.json`

###  Port Forwarding
<details>
<summary>Install Kubectl</summary>

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
```
</details>

- Download testnet cluster config from https://cloud.digitalocean.com/kubernetes/clusters
- Move the config to `$HOME/.kube/`
- Run `kubectl -n grassroots --kubeconfig=$HOME/.kube/<config_file_name>.yaml get pods`  
- Copy the name of the meta pod (e.g `cic-meta-server-67dc7c6468-8rhdq`)
- Port foward the meta pod to the local machine using `kubectl port-forward pods/<name_of_meta_pod> 6700:8000 -n grassroots --kubeconfig=$HOME/.kube/<config_file_name>.yaml`
- Clone this repository to your local machine
- Run `poetry install -E eth` in the repo root
- Open `./cic/config/testnet/config.ini` and change
  - [auth]keyfile_path 
  - [wallet]key_file
- Open a new terminal and run `poetry run cic wizard -c ./cic/config/testnet ./somewhere` 
### Tests

```
poetry run pytest
```
