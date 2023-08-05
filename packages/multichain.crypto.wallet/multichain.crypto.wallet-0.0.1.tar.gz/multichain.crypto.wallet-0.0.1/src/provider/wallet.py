from web3 import Web3


from src.function.index import Wallet


def get_token_info(eth_url, token_address,network):
    return Wallet[network].get_token_info(eth_url, token_address)
    
def get_token_balance(eth_url, token_address, address, network):
    return Wallet[network].get_balance(eth_url, token_address, address)
    
def transfer_token(eth_url, token_address, address, network):
    return Wallet[network].transfer_token(eth_url, token_address, address)

def create_account(eth_url, network):
    return Wallet[network].create_account(eth_url)

def get_address_from_key(eth_url,network, private_key):
    return Wallet[network].get_address_with_private_key(eth_url,private_key)
    
def get_chain_info(eth_url,network):
    return Wallet[network].get_chain_info(eth_url)

def get_transaction_by_hash(eth_url,network,hash):
    return Wallet[network].get_transaction_by_hash(eth_url,hash)
    
def get_transaction_count(eth_url,network,address):
    return Wallet[network].get_transaction_count(eth_url,address)
    

