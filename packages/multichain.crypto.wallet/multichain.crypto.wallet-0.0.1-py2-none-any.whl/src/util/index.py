from web3 import Web3

def get_provider(eth_url):
    return  Web3(Web3.HTTPProvider(eth_url))

def transform_address(web3, contract_address):
    return  web3.toChecksumAddress(contract_address)

def create_contract():
    ""


#   getBalance,
#   createWallet,
#   getAddressFromPrivateKey,
#   generateWalletFromMnemonic,
#   transfer,
#   getTransaction,
#   getEncryptedJsonFromPrivateKey,
#   getWalletFromEncryptedJson,
#   getTokenInfo,