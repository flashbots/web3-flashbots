from asset_information import stablecoins
from asset_information import assets
from OneINCH import OneINCH

quoter = OneINCH()
quoter.get_quote(
    assets['CVX'],
    stablecoins['FRAX'],
    str(100000 * 10**18)
)