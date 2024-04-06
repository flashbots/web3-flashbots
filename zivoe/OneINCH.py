import os
import dotenv
import requests

class OneINCH:

    def __init__(self):
        dotenv.load_dotenv()
        self.keeper_addy = os.getenv("KEEPER_0_ADDY")
        self.swapper_addy = os.getenv("SWAPPER_0_ADDY")
        self.base_url = "https://api.1inch.dev"
        self.headers_api = {
            "accept": "application/json",
            "Authorization": "Bearer " + os.getenv("ONEINCH_KEY")
        }

    def get_swap_v5(
        self,
        from_token_address: str,
        to_token_address: str,
        amount: str,
        slippage: int = 1
    ) -> dict:
        response = requests.request(
            "GET",
            self.base_url + "/swap/v5.2/1/swap",
            headers=self.headers_api,
            params={
                'src': from_token_address,
                'dst': to_token_address,
                'amount': amount,
                'from': "0x883816205341a6ba3C32AE8dAdCEbDD9d59BC2C4",
                'slippage': slippage,
                'disableEstimate': 'true',
                # 'protocols': 'SUSHI,UNISWAP_V2'
                # 'allowPartialFill': 'false',
            }
        )
        return response.json()

    def get_quote_v5(
        self,
        from_token_address: str,
        to_token_address: str,
        amount: str
    ) -> dict:
        response = requests.request(
            "GET",
            self.base_url + "/swap/v5.2/1/quote",
            headers=self.headers_api,
            params={
                'src': from_token_address,
                'dst': to_token_address,
                'amount': amount
            }
        )
        return response.json()
