import logging

from influxdb_client import InfluxDBClient

log = logging.getLogger(__name__)


class DataConnection:  # pylint: disable=too-few-public-methods
    def __init__(self, url, token, org):
        self._client = InfluxDBClient(
            url=url, token=token, org=org
        )
        log.info('connected to influx')
