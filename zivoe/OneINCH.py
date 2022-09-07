import os
import dotenv

dotenv.load_dotenv()

class OneINCH:

    def __init__(self):
        self.base_url = "https://api.1inch.io"

    def get_quote(self):
        print(self.base_url + "/v4.0/1/quote")


from EthereumAssets import stablecoins

testes = OneINCH()
testes.get_quote()