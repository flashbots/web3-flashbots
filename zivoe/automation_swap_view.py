import requests

from brownie import SwapProxy, accounts, interface, config, network, chain


def get_acc():
    if 'fork' in network.show_active():
        acc = accounts.at("0xa64cd58b0b27c80bd35c9617b5f02d16b9ba380d", force=True)
    else:
        acc = accounts.add(
            config['wallets']['from_key']
        )
    return acc


def main():
    active_network = config["networks"][network.show_active()]

    acc = get_acc()

    print('Getting ProxySwap contract...')

    try:
        swap_proxy = SwapProxy[len(SwapProxy) - 1]  # Get the latest SwapProxy contract deployed
    except IndexError:
        swap_proxy_addr = input('SwapProxy address: ')
        swap_proxy = SwapProxy.at(swap_proxy_addr)

    token_in = interface.IERC20Metadata(active_network['tokenIn'])
    token_out = interface.IERC20Metadata(active_network['tokenOut'])
    amount = active_network['amount']
    slippage = active_network['slippage']
    chain_id = active_network['chain_id']

    swap_req = requests.get(
        f'https://api.1inch.exchange/v3.0/{chain_id}/swap?fromTokenAddress={token_in}&toTokenAddress={token_out}&amount={amount}&fromAddress={swap_proxy}&slippage={slippage}&destReceiver={acc}&disableEstimate=true'
    ).json()

    swap_data = swap_req['tx']['data']
    min_out = int(swap_req['toTokenAmount']) * (100 - slippage) / 100

    confirm = input(
        f"Quote: {amount / 10 ** token_in.decimals()} {token_in.symbol()} -> {min_out / 10 ** token_out.decimals()} {token_out.symbol()} (MINIMUM RECEIVED) (y/n)")
    if confirm.lower() != 'y':
        min_out = float(input('Minimum received (e.g 500e18): '))

    token_in.approve(swap_proxy, amount, {'from': acc})

    print(f'Token [IN] balance before Swap: {token_in.balanceOf(acc)}')
    print(f'Token [OUT] balance before Swap: {token_out.balanceOf(acc)}')

    swap_proxy.swap(min_out, swap_data, {'from': acc})

    print(f'Token [IN] balance after Swap: {token_in.balanceOf(acc)}')
    print(f'Token [OUT] balance after Swap: {token_out.balanceOf(acc)}')