import logging

from algo.data.reader import PriceStream
from algo.indicator import MAverage
from algo.trading import CurrentState, OrderType, PricePoint

from .common import BaseStrategyParams, TradingResult


class MAStrategyParams(BaseStrategyParams):
    first_avg_length: int
    second_avg_length: int


log = logging.getLogger(__name__)


def act(data_stream: PriceStream, params: MAStrategyParams) -> TradingResult:
    (mavg1_len, mavg2_len) = params
    mavg1 = MAverage(mavg1_len)
    mavg2 = MAverage(mavg2_len)
    state = CurrentState()
    trades = []
    history_price: PricePoint
    for history_price in data_stream:
        mavg1.tick(history_price.bid)
        mavg2.tick(history_price.bid)
        log.debug('price data %s, mavg1: %s:%s', history_price, mavg1, mavg2)
        expected_direction = None  # kind of expected behaviour

        if not (mavg1.ready() and mavg2.ready()):
            # skipping before ready
            continue

        if mavg1.value > mavg2.value:
            expected_direction = OrderType.BUY
        else:
            expected_direction = OrderType.SELL

        # if state.in_market and state.order_type == expected_direction:
        #     # all good nothing to do here
        #     continue
        # el
        if state.in_market and state.order_type != expected_direction:
            trade = state.close(history_price)
            trades.append(
                trade
            )
            log.info('closing trade %s', trade)
        elif not state.in_market:
            state.open(history_price, expected_direction)
            log.info('open trade %s', state)

    total_profit = sum(tr.profit for tr in trades)
    total_expenses = sum(tr.trade_expenses for tr in trades)
    num_of_trades = len(trades)
    log.info('simulation total',
             extra={
                 'trades_len': num_of_trades,
                 'total_profit': total_profit,
                 'sum_of_expenses': total_expenses
             })
    return TradingResult(total_profit, total_expenses, num_of_trades)
