import requests
from termcolor import cprint

from network import Networks

def trade(network, tf: str, tt: str, amount: int, wallet_address: str):
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

    match (network):
        case Networks.POLYGON:
            headers['liquidityzone'] = 'matic'
        case Networks.ARBITRUM:
            json['forcedDexes'] = 'univ3_arbitrum'
            headers['liquidityzone'] = 'arbitrum'
        case Networks.OPTIMISM:
            json['forcedDexes'] = 'univ3_optimism'
            headers['liquidityzone'] = 'optimism'

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
