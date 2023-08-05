from web3 import Web3
import json
from src.util.index import get_provider, transform_address
erc_20_abi = json.load(open('src/abi/erc_20.json'))

def get_token_info(eth_url,contract_address):
          web3 = get_provider(eth_url)
          contract_address = transform_address(web3, contract_address)
          contract = web3.eth.contract(address=contract_address, abi=erc_20_abi)
          return  {
              "name": contract.functions.name().call(),
              "symbol": contract.functions.symbol().call(),
              "decimals": contract.functions.decimals().call(),
              "total_supply": contract.functions.totalSupply().call(),
          }

def get_balance(eth_url,contract_address,address):
          web3 = get_provider(eth_url)
          contract_address = transform_address(web3, contract_address)
          address = transform_address(web3, contract_address)
          contract = web3.eth.contract(address=contract_address, abi=erc_20_abi)
          return contract.functions.balanceOf(address).call()

def create_account(eth_url):
          web3 = get_provider(eth_url)
          account = web3.eth.account.create()
          return {
              "address":account._address,
              "private_key":account._private_key,
              }


def get_address_with_private_key(eth_url, private_key):
          web3 = get_provider(eth_url)
          return  web3.eth.account.from_key(private_key).address

def get_chain_info(eth_url):
          web3 = get_provider(eth_url)
          return {
            "gas_price": web3.eth.gas_price,
            "chain_id": web3.eth.chain_id,
            }
            
def get_transaction_by_hash(eth_url,hash):
          web3 = get_provider(eth_url)
          return web3.toJSON(web3.eth.get_transaction(hash))

def get_transaction_count(eth_url,address):
          web3 = get_provider(eth_url)
          address = transform_address(web3, address)
          return web3.eth.get_transaction_count(address)