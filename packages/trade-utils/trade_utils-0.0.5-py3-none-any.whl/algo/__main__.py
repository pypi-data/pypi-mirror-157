#!/usr/bin/python3

import logging.config

from algo.config import config
from algo.constant import Symbol
from algo.simulation import simulate_trading
from algo.strategy import moving_average_sample
from algo.util import d

logging.config.fileConfig(
    './logging.conf',
    # TBD: figure out why lack of the following line disables logging inside module
    disable_existing_loggers=False
)


if __name__ == '__main__':

    log = logging.getLogger(__name__)
    log.info('playground home will be here')

    # strategy = moving_average_sample
    # result = simulate_trading(
    #     '2022-06-07',
    #     Symbol.JPY,
    #     strategy.module,
    #     strategy.args(2, 3)
    # )
    # log.info('simulation-complete', extra={'result': result})
    # result = 1
    # log.info('vars formatter ', extra=d(result))
