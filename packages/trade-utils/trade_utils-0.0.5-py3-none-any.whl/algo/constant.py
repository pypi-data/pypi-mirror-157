from enum import Enum


class Symbol(Enum):
    JPY = 'USD_JPY'
    GBP = 'EUR_USD'
    EUR = 'GBP_USD'
    AUD = 'AUD_USD'
    GOLD = 'XAU_USD'
    BTC = 'BTC_USD'
    CORN = 'CORN_USD'
    WHEAT = 'WHEAT_USD'
    NAS100_USD = 'NAS100_USD'

    @classmethod
    def all_values(cls, glue: str = ','):
        return glue.join(
            map(lambda x: x.value, cls)
        )
