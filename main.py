import random
import time
from termcolor import cprint
from web3 import Web3
from web3.middleware import geth_poa_middleware

import config
import keys_utils
import slingshot
import token_utils
from network import Networks
from networks import arbitrum, polygon, optimism

if __name__ == '__main__':
    network = Networks(config.NETWORK)
    match(network): 
        case Networks.POLYGON: network_data = polygon.DATA
        case Networks.ARBITRUM: network_data = arbitrum.DATA
        case Networks.OPTIMISM: network_data = optimism.DATA

    w3 = Web3(Web3.HTTPProvider(network_data['RPC']))
    if (network == Networks.POLYGON):
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    slingshot_abi = '[{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"components":[{"internalType":"address","name":"moduleAddress","type":"address"},{"internalType":"bytes","name":"encodedCalldata","type":"bytes"}],"name":"trades","type":"tuple[]"},{"internalType":"uint256","name":"finalAmountMin","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"name":"executeTrades","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
    slingshot_contract = w3.eth.contract(address=network_data['SLINGSHOT_CONTRACT_ADDRESS'], abi=slingshot_abi)
    token_contract = token_utils.getTokenContract(w3.toChecksumAddress(config.TOKEN_FROM), w3)

    keys = keys_utils.getKeys(config.PKS_FILE)
    cprint(f'+ {len(keys)} keys found', 'cyan')
    accounts = list(keys_utils.getAccounts(w3, keys).items())
    cprint(f'+ {len(accounts)} accounts found', 'cyan')
    random.shuffle(accounts)

    for (pk, wallet_address) in accounts:
        print(f'\n>>> Start swap for address {wallet_address}')
        try:
            amount = random.randint(config.AMOUNT_MIN, config.AMOUNT_MAX)
            value = 0
            if (config.TOKEN_FROM == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'): 
                value = amount
            else:
                spender_address = w3.toChecksumAddress(network_data['APPROVE_CONTRACT'])
                allowance = token_utils.checkAllowance( 
                    token_contract=token_contract,
                    wallet_address=w3.toChecksumAddress(wallet_address),
                    spender_address=spender_address,
                )
                if not allowance:   
                    print(f'>>> Approving token spend for address {wallet_address}')
                    approve_tx_hash = token_utils.approveTokenSpend(
                        token_contract=token_contract,
                        wallet_address=w3.toChecksumAddress(wallet_address),
                        spender_address=spender_address,
                        pk=pk,
                        w3=w3,
                    )
                    cprint(f'>>> APPROVED: {network_data["SCANNER"]}{w3.toHex(approve_tx_hash)}', 'green')

            response = slingshot.trade(   
                network=network,
                tf=config.TOKEN_FROM, 
                tt=config.TOKEN_TO, 
                amount=amount,
                wallet_address=wallet_address,
            )

            if network == Networks.POLYGON:
                estimatedOutput = int(response['estimatedOutput'])
                finalAmountMin = int(estimatedOutput - estimatedOutput * config.SLIPPAGE)
                txn = slingshot_contract.functions.executeTrades(
                    w3.toChecksumAddress(config.TOKEN_FROM),
                    w3.toChecksumAddress(config.TOKEN_TO),
                    amount,
                    [
                        {
                            'moduleAddress': w3.toChecksumAddress(network_data['SUSHI_MODULE_ADDRESS']),
                            'encodedCalldata': slingshot.encodeSushi(
                                tf=config.TOKEN_FROM,
                                tt=config.TOKEN_TO,
                                amount=amount,
                            )
                        },
                    ],
                    finalAmountMin,
                    w3.toChecksumAddress(wallet_address),
                ).buildTransaction({
                        'type': '0x2',
                        'from': w3.toChecksumAddress(wallet_address),
                        'value': value,
                        'gas': int(response['gasEstimate']),
                        'nonce': w3.eth.getTransactionCount(wallet_address),
                    })
            else:
                txn = {
                    'data': response['txData'],
                    'gas': int(response['gasEstimate']),
                    'chainId': network_data['CHAIN_ID'],
                    'from': w3.toChecksumAddress(wallet_address),
                    'value': value,
                    'gasPrice': w3.eth.gas_price,
                    'nonce': w3.eth.getTransactionCount(wallet_address),
                    'to': network_data['SLINGSHOT_CONTRACT_ADDRESS']
                }

            signed_txn = w3.eth.account.sign_transaction(txn, private_key=pk)
            tx_hash = w3.eth.send_raw_transaction(w3.toHex(signed_txn.rawTransaction))
            cprint(f'>>> SUCCESS: {network_data["SCANNER"]}{w3.toHex(tx_hash)}', 'green')

            sleeping_secs = random.randint(5, 15)
            print(f'>>> Sleeping for {sleeping_secs} seconds...')
            time.sleep(sleeping_secs)
        except Exception as e:
            cprint(f'>>> Error occured while swapping for address {wallet_address}: {e}', 'red')
