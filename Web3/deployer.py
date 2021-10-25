from solcx import compile_standard
from web3 import Web3
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    file = open('./SimpleStorage.sol', 'r')
    simple_storage = file.read()
    file.close()
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {
            "SimpleStorage.sol": {
                "content": simple_storage
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
        solc_version="0.6.0")

    bytecode = compiled["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
    abi = compiled["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    chain_id = 1337
    my_address = os.environ.get('MY_ADDRESS')
    private_key = os.environ.get('PRIVATE_KEY')

    simple_storage_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.getTransactionCount(my_address)

    # 1. build a transaction
    # 2. Sign the transaction
    # 3. Send a transaction
    transaction = simple_storage_contract.constructor().buildTransaction({
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce
    })

    signed = w3.eth.account.sign_transaction(transaction, private_key)
    t_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    t_receipt = w3.eth.wait_for_transaction_receipt(t_hash)


    #working with contracts
    simple_storage_c = w3.eth.contract(address=t_receipt.contractAddress, abi=abi)
    simple_storage_c.functions.store(15).call()
    print(simple_storage_c.functions.retrieve().call())

    store_transaction = simple_storage_c.functions.store(15).buildTransaction({
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1
    })
    signed_store = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
    store_hash = w3.eth.sendRawTransaction(signed_store.rawTransaction)
    store_receipt = w3.eth.wait_for_transaction_receipt(store_hash)
    print(simple_storage_c.functions.retrieve().call())

    
if __name__ == '__main__':
    main()
