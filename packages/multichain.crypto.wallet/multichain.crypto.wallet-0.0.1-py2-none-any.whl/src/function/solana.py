# from solana import 
# import json
# erc_20_abi = json.load(open('src/abi/erc_20.json'))


# def get_name(eth_url,contract_address):
#           provider = Web3.HTTPProvider(eth_url)
#           web3 = Web3(provider)
#           contract_address = web3.toChecksumAddress(contract_address)
#           return web3.eth.contract(address=contract_address, abi=erc_20_abi).functions.name().call()
#         #   return await contract.functions.name().call()


# def get_balance(eth_url,contract_address,address):
#           provider = Web3.HTTPProvider(eth_url)
#           web3 = Web3(provider)
#           contract_address = web3.toChecksumAddress(contract_address)
#           address = web3.toChecksumAddress(address)
#           contract = web3.eth.contract(address=contract_address, abi=erc_20_abi)
#           return contract.functions.balanceOf(address).call()

