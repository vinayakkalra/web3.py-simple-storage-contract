from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

install_solc("0.6.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
infura_key = os.getenv("INFURA_KEY")
# for connecting to http provider
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/" + infura_key))
chain_id = 4
my_address = os.getenv("ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# create a transaction
# sign a transaction
# send a transaction

transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)

# contract deployed successfully

# working with contract
# contract address
# contarct abi

simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)
# call  - dont make a state change
#  transact - make a state change
print(simple_storage.functions.retrieve().call())
print(simple_storage.functions.store(15).call())  # calling is just a simulation
print(simple_storage.functions.retrieve().call())  # value is not set here

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

store_tx_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_tx_reciept = w3.eth.wait_for_transaction_receipt(store_tx_hash)
print(simple_storage.functions.retrieve().call())
