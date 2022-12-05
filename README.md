# slingshot-swap
Script for swaping on Slingshot exchange. Currently under development.

## Features
- swaps on Slingshot with Sushi
- swaps fixed amount from USDT to USDC
- currently only Polygon network

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

To change swapping amount edit `AMOUNT_TO_SWAP` field in `config.py` file:
```python
AMOUNT_TO_SWAP = YOUR_VALUE
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
