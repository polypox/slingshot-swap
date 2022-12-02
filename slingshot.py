import requests
from termcolor import cprint
from web3 import Web3
from web3.middleware import geth_poa_middleware

### Insert your private key
pk = ''

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
    return requests.post(url=url, json=json).json()

def encodeSushi(tf: str, tt: str, amount: int) -> str:
    return (
        '0xef5dab3a'
        + amount.to_bytes(32, 'big').hex()
        + '0000000000000000000000000000000000000000000000000000000000000080'
        + '00000000000000000000000000000000000000000000000000000000000000e0'
        + '0000000000000000000000000000000000000000000000000000000000000001'
        + '0000000000000000000000000000000000000000000000000000000000000002'
        + '0'*(64-len(tf))+tf
        + '0'*(64-len(tt))+tt
        + '0000000000000000000000000000000000000000000000000000000000000001'
        + '00000000000000000000000000000000000000000000000000000000000001f4'
    )

rpc = 'https://polygon-rpc.com'

contract_address = '0x07e56b727e0EAcFa53823977599905024c2de4F0'
abi = '[{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"components":[{"internalType":"address","name":"moduleAddress","type":"address"},{"internalType":"bytes","name":"encodedCalldata","type":"bytes"}],"name":"trades","type":"tuple[]"},{"internalType":"uint256","name":"finalAmountMin","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"name":"executeTrades","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

usdt_address = 'c2132d05d31c914a87c6611c10748aeb04b58e8f'
usdc_address = '2791bca1f2de4661ed88a30c99a7a9449aa84174'

sushi_address = '2cf2c0e22787a19e797a4ea4a8723f98f7f49a4e'

amount = 1500000
slippage = 0.01

w3 = Web3(Web3.HTTPProvider(rpc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = w3.eth.contract(address=contract_address, abi=abi)

wallet = w3.eth.account.from_key(pk)
wallet_address = wallet.address

nonce = w3.eth.getTransactionCount(wallet_address)

response = trade(
    tf='0x'+usdt_address, 
    tt='0x'+usdc_address, 
    amount=amount,
    wallet_address=wallet_address,
)

estimatedOutput = int(response['estimatedOutput'])
finalAmountMin = int(estimatedOutput - estimatedOutput * slippage)

txn = contract.functions.executeTrades(
    w3.toChecksumAddress(usdt_address),
    w3.toChecksumAddress(usdc_address),
    amount,
    [
        {
            'moduleAddress': w3.toChecksumAddress(sushi_address),
            'encodedCalldata': encodeSushi(
                tf=usdt_address,
                tt=usdc_address,
                amount=amount,
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

signed_txn = w3.eth.account.sign_transaction(txn, private_key=pk)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
cprint(f'\nSUCCESS: https://polygonscan.com/tx/{w3.toHex(tx_hash)}', 'green')
