from asset_information import stablecoins
from asset_information import assets
from OneINCH import OneINCH

api = OneINCH()

fromToken = stablecoins['USDC']
toToken = stablecoins['DAI']
amount = str(200000 * 10**6)

quote = api.get_quote_v5(
    fromToken,
    toToken,
    amount
)

print(quote)

swap = api.get_swap_v5(
    fromToken,
    toToken,
    amount
)

print(swap)





'''
struct SwapDescription {
    IERC20 srcToken;
    IERC20 dstToken;
    address payable srcReceiver;
    address payable dstReceiver;
    uint256 amount;
    uint256 minReturnAmount;
    uint256 flags;
    bytes permit;
}
'''
