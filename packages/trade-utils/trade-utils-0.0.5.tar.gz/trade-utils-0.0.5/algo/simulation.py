import logging

from algo.constant import Symbol
from algo.data.reader import get_data_reader
from algo.strategy.common import BaseStrategyParams, Strategy

log = logging.getLogger(__name__)


def simulate_trading(simulation_date: str, symbol: Symbol, strategy: Strategy, params: BaseStrategyParams):
    log.info('start simulation')
    data_reader = get_data_reader()
    data_iterator = data_reader.hour_data(simulation_date, symbol)
    result = strategy(data_iterator, params)
    log.info('simulation result', extra={'simulation-result': result})
    return result
