def getTokenContract(token_address, w3):
    token_abi = '[{"inputs":[{"internalType":"address","type":"address"},{"internalType":"address","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","type":"address"},{"internalType":"uint256","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'
    token_contract = w3.eth.contract(address=token_address, abi=token_abi)
    return token_contract

def checkAllowance(token_contract, wallet_address, spender_address):
    allowance = token_contract.functions.allowance(
        wallet_address,
        spender_address,
    ).call()
    return allowance

def approveTokenSpend(token_contract, wallet_address, spender_address, pk, w3):
    nonce = w3.eth.getTransactionCount(wallet_address)
    approve_txn = token_contract.functions.approve(
        spender_address,
        16**64-1
    ).buildTransaction({
        'from': wallet_address, 
        'nonce': nonce,
        'gasPrice': w3.eth.gas_price,
    })
    gas = w3.eth.estimate_gas(approve_txn)
    approve_txn['gas'] = gas

    signed_tx = w3.eth.account.signTransaction(approve_txn, pk)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_hash
