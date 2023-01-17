from asset_information import stablecoins
from asset_information import assets
from OneINCH import OneINCH

api = OneINCH()

fromToken = stablecoins['DAI']
toToken = stablecoins['FRAX']
amount = str(5000 * 10**18)

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
