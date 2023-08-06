import logging

from influxdb_client.client.write_api import SYNCHRONOUS
from v20.pricing import ClientPrice  # donno when v2 was installed ...

from ..config import config
from .connection import DataConnection

log = logging.getLogger(__name__)


class DataReporter(DataConnection):  # pylint: disable=too-few-public-methods
    def __init__(self, url, token, org):
        super().__init__(url, token, org)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

    def report(self, price: ClientPrice):
        if len(price.bids) == 0 or len(price.asks) == 0:
            log.info('no-price-data')
            log.error('unexpected-price-datapoint', extra=dir(price))
            return
        json_body = [
            {
                "measurement": 'price',
                "tags": {
                    "instrument": price.instrument,
                },
                "time": price.time,
                "fields": {
                    "bid": price.bids[0].price,
                    "ask": price.asks[0].price,
                }
            }
        ]
        self._write_api.write(bucket='tsdata', record=json_body)
        log.info('data sent')


def get_data_reporter() -> DataReporter:
    return DataReporter(
        config.influx_url,
        config.influx_token,
        config.influx_org
    )
