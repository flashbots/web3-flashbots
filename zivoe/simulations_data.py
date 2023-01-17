from asset_information import stablecoins
from asset_information import assets
from OneINCH import OneINCH

api = OneINCH()

base_frax_amt = 22191780821917808219178

amounts_frax = [
    str(base_frax_amt),
    str(base_frax_amt * 2),
    str(base_frax_amt * 3)
]

base_usdc_amt = 22191780821

amounts_usdc = [
    str(base_usdc_amt),
    str(base_usdc_amt * 2),
    str(base_usdc_amt * 3)
]

for swap_frax in range(0, 3):
    fromToken = stablecoins['FRAX']
    toToken = stablecoins['DAI']
    quote = api.get_quote(fromToken, toToken, amounts_frax[swap_frax])
    swap = api.get_swap(fromToken, toToken, amounts_frax[swap_frax])
    print('swap_frax', swap_frax, swap['tx']['data'][2:])

for swap_usdc in range(0, 3):
    fromToken = stablecoins['USDC']
    toToken = stablecoins['DAI']
    quote = api.get_quote(fromToken, toToken, amounts_usdc[swap_usdc])
    swap = api.get_swap(fromToken, toToken, amounts_usdc[swap_usdc])
    print('swap_usdc', swap_usdc, swap['tx']['data'][2:])









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
