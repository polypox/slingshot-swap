from termcolor import cprint

def getKeys(file_name: str) -> list:
    keys = []
    with open(file_name) as keys_file:
        for line in keys_file:
            key = line.strip()
            if (key):
                keys.append(key)
    return keys

def getAccounts(w3, keys: list) -> dict:
    accounts = {}
    for pk in keys:
        try:
            wallet_address = w3.eth.account.from_key(pk).address
        except Exception as e:
            cprint(f'ERROR occured while initializing account from private key \"{pk}\": {e}', 'red')
        accounts[pk] = wallet_address
    return accounts
