from asset_information import stablecoins
from asset_information import assets
from OneINCH import OneINCH

api = OneINCH()

fromToken = assets['RLM']
toToken = assets['WETH']
amount = str(700 * 10**18)

quote = api.get_quote(
    fromToken,
    toToken,
    amount
)

swap = api.get_swap(
    fromToken,
    toToken,
    amount
)

print(quote)
print(swap)