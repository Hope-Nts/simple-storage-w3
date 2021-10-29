from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()

#reading the simplestorage file so that the compiler knows what to load
with open("./SimpleStorage.sol", "r") as file:
  simple_storage_file = file.read()
  #print(simple_storage_file)

# We add these two lines that we forgot from the video!
#print("Installing...")
install_solc("0.6.0")

# #compiling the file using py-solc-x
# compiled_sol = compile_standard(
#   {
#     "language": "Solidity",
#     "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
#     "settings":{
#       "outputSelection": {
#         "*": {"*": ["abi", "evm.byteccode", "evm.sourceMap"]}
#       }
#     },
#   },
#   solc_version="0.6.0",
# )

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

#print(compiled_sol)

#writing the compiled code to another file
with open("compiled_code.json", "w") as file:
  json.dump(compiled_sol, file)

#we need the abi and the bytecode when deploying the contract

#deploying in python
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

#getting the abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

#connecting to ganache
network_id = os.getenv( "NETWORK_ID")
w3 = Web3(Web3.HTTPProvider(network_id))
chain_id = 4 #from chainid.network
# chain_id = 5777esdae

# w3 = Web3(Web3.HTTPProvider("http://0.0.0.0:8545"))


#we get this from ganache any of the random generated addresses
my_address = "0x6003Ce38C76A15390663DbD13D5b357ec5f2dE64"
# when ever we add a private key to python we're going to need to add the 0x because it need hex value
private_key = os.getenv( "PRIVATE_KEY")


# Creating the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
print(SimpleStorage)
# print(private_key)

# To deploy this contract, there are three tasks to done
# 1. Build the Contract Deploy Transaction
# 2. Sign the Transaction
# 3. Send the Transaction

#getting the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
#print(nonce)

# building a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce }
)
#print(transaction)

#signing the txn
signed_txn = w3.eth.account.sign_transaction(transaction, private_key = private_key)
#print(signed_txn)

#sending the signed tansaction
print("Deploying Contract ........")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Note: when sending transactions we should always wait
# the code below stops and waits for the transaction to go through
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Deployed")
#working with contracts, we need 2 things
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address= tx_receipt.contractAddress, abi= abi)

#we can interact with contracts in 2 ways
# Call -> simulate making the call and getting a return value,they don't make a state change
# Transact -> actually make a state change

#initial value of favorite number
print(simple_storage.functions.retrieve().call())

#changing the value of _favoriteNumber
#print(simple_storage.functions.store(15).call())
#using call doesn't change the state of the blockchain

#building a new transaction to store value
print("Updating Contract ......")
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id, "from": my_address, "nonce": nonce + 1
})
# we're incrementing the nonce because each transaction can only have 1 unique nonce 
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key = private_key
    )

send_store_txn = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
transaction_reciept = w3.eth.wait_for_transaction_receipt(send_store_txn)

#printing the newly deployed value
print("Updated")
print(simple_storage.functions.retrieve().call())
print(simple_storage.functions.retrieve().call())