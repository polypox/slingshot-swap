# slingshot-swap
Script for swaping on Slingshot exchange. Currently under development.

## Features
- swaps on Slingshot with Sushi
- swaps specified amount of specified tokens
- supports Polygon and Arbitrum networks

## How to use
Before running the script, insert your private keys in `private_keys.txt` file one by one without quotation marks:
```
1111111111111111 #first private key
2222222222222222 #second private ky
...
1263784787657878
```
### Config
To change network edit `NETWORK` field in `config.py` file:
```python
NETWORK = YOUR_NETWORK # 0 - Polygon | 1 - Arbitrum
```

To change swapping amount range edit `AMOUNT_MIN`/`AMOUNT_MAX` fields in `config.py` file:
```python
AMOUNT_MIN = YOUR_VALUE_1 # min amount, for example 10000
AMOUNT_MAX = YOUR_VALUE_2 # max amount, for example 20000
```

To change slippage edit `SLIPPAGE` field in `config.py` file:
```python
SLIPPAGE = YOUR_SLIPPAGE # float value between 0.0 and 1.0
```
**Before running the script please make sure you have sufficient balance**

## Plans
- [x] Arbitrum support
- [x] multiple accounts support
- [ ] more tokens
