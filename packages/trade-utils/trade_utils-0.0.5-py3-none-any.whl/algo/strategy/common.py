from typing import Callable, NamedTuple

from algo.data.reader import PriceStream

# for now moeny are float... hopefully they will start soaring soon :rofl:
Money = float


class TradingResult(NamedTuple):
    profit: Money
    expenses: Money
    number_of_trades: int


BaseStrategyParams = NamedTuple


Strategy = Callable[[PriceStream, BaseStrategyParams], TradingResult]


class StrategyDescriptor(NamedTuple):
    name: str
    module: Strategy
    args: BaseStrategyParams
    description: str
