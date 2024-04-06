from asset_information import stablecoins
from asset_information import assets
from OneINCH import OneINCH

api = OneINCH()

fromToken = stablecoins['USDC']
toToken = stablecoins['PYUSD']
amount = str(100_000 * 10**6)

swap = api.get_swap_v5(
    fromToken,
    toToken,
    amount
)

print(swap)
