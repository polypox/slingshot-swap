import requests
from enum import Enum
from termcolor import cprint
from web3 import Web3
from web3.middleware import geth_poa_middleware
import config
from network import Networks
from networks import arbitrum, polygon

network = Networks(config.NETWORK)
match(network):
    case Networks.POLYGON: network_data = polygon.DATA
    case Networks.ARBITRUM: network_data = arbitrum.DATA

def trade(tf: str, tt: str, amount: int, wallet_address: str):
    url = 'https://slingshot.finance/api/v3/trade/'
    json = {
        'from': tf,
        'fromAmount': str(amount),
        'gasOptimized': False,
        'limit': "99",
        'recipient': wallet_address,
        'threeHop': True,
        'to': tt,
        '_unsafe': False,
    }
    headers = {}

    if (network == Networks.ARBITRUM):
        json['forcedDexes'] = 'univ3_arbitrum'
        headers['liquidityzone'] = 'arbitrum'

    return requests.post(url=url, json=json, headers=headers).json()

def encodeSushi(tf: str, tt: str, amount: int) -> str:
    tf_formated = tf[2:]
    tt_formated = tt[2:]
    return (
        '0xef5dab3a'
        + amount.to_bytes(32, 'big').hex()
        + '0000000000000000000000000000000000000000000000000000000000000080'
        + '00000000000000000000000000000000000000000000000000000000000000e0'
        + '0000000000000000000000000000000000000000000000000000000000000001'
        + '0000000000000000000000000000000000000000000000000000000000000002'
        + '0'*(64-len(tf_formated))+tf_formated
        + '0'*(64-len(tt_formated))+tt_formated
        + '0000000000000000000000000000000000000000000000000000000000000001'
        + '00000000000000000000000000000000000000000000000000000000000001f4'
    )

w3 = Web3(Web3.HTTPProvider(network_data['RPC']))
if (network == Networks.POLYGON):
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

slingshot_abi = '[{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"components":[{"internalType":"address","name":"moduleAddress","type":"address"},{"internalType":"bytes","name":"encodedCalldata","type":"bytes"}],"name":"trades","type":"tuple[]"},{"internalType":"uint256","name":"finalAmountMin","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"name":"executeTrades","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
contract = w3.eth.contract(address=network_data['SLINGSHOT_CONTRACT_ADDRESS'], abi=slingshot_abi)

wallet = w3.eth.account.from_key(config.PK)
wallet_address = wallet.address

response = trade(
    tf=config.TOKEN_FROM, 
    tt=config.TOKEN_TO, 
    amount=config.AMOUNT_TO_SWAP,
    wallet_address=wallet_address,
)

nonce = w3.eth.getTransactionCount(wallet_address)

match network:
    case Networks.POLYGON:
        estimatedOutput = int(response['estimatedOutput'])
        finalAmountMin = int(estimatedOutput - estimatedOutput * config.SLIPAGE)
        txn = contract.functions.executeTrades(
            w3.toChecksumAddress(config.TOKEN_FROM),
            w3.toChecksumAddress(config.TOKEN_TO),
            config.AMOUNT_TO_SWAP,
            [
                {
                    'moduleAddress': w3.toChecksumAddress(network_data['SUSHI_MODULE_ADDRESS']),
                    'encodedCalldata': encodeSushi(
                        tf=config.TOKEN_FROM,
                        tt=config.TOKEN_TO,
                        amount=config.AMOUNT_TO_SWAP,
                    )
                },
            ],
            finalAmountMin,
            w3.toChecksumAddress(wallet_address),
        ).buildTransaction({
                'type': '0x2',
                'from': w3.toChecksumAddress(wallet_address),
                'value': 0,
                'gas': int(response['gasEstimate']),
                'nonce': nonce,
            })
    case Networks.ARBITRUM:
        txn = {
            'data': response['txData'],
            'gas': int(response['gasEstimate']),
            'chainId': 42161,
            'from': w3.toChecksumAddress(wallet_address),
            'value': 0,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
            'to': network_data['SLINGSHOT_CONTRACT_ADDRESS']
        }

signed_txn = w3.eth.account.sign_transaction(txn, private_key=config.PK)
tx_hash = w3.eth.send_raw_transaction(w3.toHex(signed_txn.rawTransaction))
cprint(f'\nSUCCESS: {network_data["SCANNER"]}{w3.toHex(tx_hash)}', 'green')
