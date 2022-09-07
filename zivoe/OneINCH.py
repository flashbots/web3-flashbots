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
        protocols: str = 'all',
        fee: str = '1',
        connector_tokens: int = 3,  # Max 5
        complexity_level: int = 2
    ) -> dict:
        print(self.base_url + "/v4.0/1/quote")
        print(self.from_token_address)
        print(self.to_token_address)
        response = requests.request(
            "GET",
            self.base_url + "/v4.0/1/quote",
            headers=self.headers_api,
            params={
                'fromTokenAddress': from_token_address,
                'toTokenAddress': to_token_address,
                'amount': amount,
                # 'protocols': protocols,
                # 'fee': fee,
                # 'connectorTokens': connector_tokens,
                'complexityLevel': complexity_level,
            }
        )
        print(response.json())
        return {}


from EthereumAssets import stablecoins
from EthereumAssets import assets

testes = OneINCH()
testes.get_quote(
    assets['CRV'],
    stablecoins['FRAX'],
    str(100000 * 10**18)
)