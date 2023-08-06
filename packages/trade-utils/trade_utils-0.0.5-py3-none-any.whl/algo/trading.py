from collections import namedtuple
from enum import Enum

PricePoint = namedtuple('PricePoint', 'time ask bid')


class OrderType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class TradeResult(object):
    # TBD: make it named tuple
    def __init__(self, trade_profit: float, trade_expenses: float) -> None:
        self.trade_profit = trade_profit
        self.trade_expenses = trade_expenses

    @property
    def profit(self):
        return self.trade_profit - self.trade_expenses

    def __str__(self) -> str:
        return f'<TradeResult({self.profit}):\t{self.trade_profit}\t{self.trade_expenses})>'


class CurrentState(object):
    def __init__(self) -> None:
        self._in_market = False
        self._open_price: float = None
        self._order_type: OrderType = None
        self._sl_size: float
        self.is_sl_close: bool = False

    @property
    def in_market(self) -> bool:
        return self._in_market

    @property
    def order_type(self) -> OrderType:
        return self._order_type

    def open(self, price_point: PricePoint, order_type: OrderType, sl_size=None):
        self._in_market = True
        self._order_type = order_type
        self._open_price = price_point.bid
        self._sl_size = sl_size
        self.is_sl_close = False

    def is_sl_time(self, price_point: PricePoint):
        """stop loss is negative .... why the hell not :) """
        return self.current_profit(price_point) < self._sl_size

    def current_profit(self, price_point: PricePoint) -> float:
        profit = self._open_price - price_point.bid
        if self._order_type != OrderType.SELL:
            profit *= -1
        return profit

    def close(self, price_point: PricePoint) -> TradeResult:
        """ close the trade and return profit"""
        self._in_market = False
        return TradeResult(
            self.current_profit(price_point),
            price_point.ask - price_point.bid
        )

    def __str__(self) -> str:
        return f'<State: order: {self.order_type}, open: {self._open_price}>'
