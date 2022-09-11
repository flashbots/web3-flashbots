import os
import dotenv
import requests

class OneINCH:

    def __init__(self):
        dotenv.load_dotenv()
        self.keeper_addy = os.getenv("KEEPER_0_ADDY")
        self.swapper_addy = os.getenv("SWAPPER_0_ADDY")
        self.base_url = "https://api.1inch.io"
        self.headers_api = {
            "Accept": "application/json"
        }

    def get_quote(
        self,
        from_token_address: str,
        to_token_address: str,
        amount: str,
        complexity_level: str = '2'
    ) -> dict:
        response = requests.request(
            "GET",
            self.base_url + "/v4.0/1/quote",
            headers=self.headers_api,
            params={
                'fromTokenAddress': from_token_address,
                'toTokenAddress': to_token_address,
                'amount': amount,
                'complexityLevel': complexity_level,
            }
        )
        return response.json()

    def get_swap_low(
        self, chain_id, token_in, token_out, amount, swap_proxy, slippage, destReceiver
    ):
        swap_req = requests.get(
            f'https://api.1inch.exchange/v4.0/{chain_id}/swap?fromTokenAddress={token_in}&toTokenAddress={token_out}&amount={amount}&fromAddress={swap_proxy}&slippage={slippage}&destReceiver={destReceiver}&disableEstimate=true'
        ).json()
        return swap_req

    def get_swap(
        self,
        from_token_address: str,
        to_token_address: str,
        amount: str,
        slippage: int = 0.3,
    ) -> dict:
        response = requests.request(
            "GET",
            self.base_url + "/v4.0/1/swap",
            headers=self.headers_api,
            params={
                'fromTokenAddress': from_token_address,
                'toTokenAddress': to_token_address,
                'fromAddress': "0x9fA34593Ea2b18bc48FD4604A6Cc49c92b337efe",
                'disableEstimate': 'true',
                'slippage': slippage,
                'amount': amount,
            }
        )
        return response.json()
