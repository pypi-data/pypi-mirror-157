import logging
from datetime import datetime, timedelta
from typing import Generator

from influxdb.resultset import ResultSet

from ..config import config
from ..constant import Symbol
from ..trading import PricePoint
from .connection import DataConnection

log = logging.getLogger(__name__)

PriceStream = Generator[PricePoint, None, None]


class DataReader(DataConnection):
    def __init__(self, url, token, org):
        super().__init__(url, token, org)
        self._query_api = self._client.query_api()

    def hour_data(self, date_str: str, symbol: Symbol) -> PriceStream:
        start = datetime.fromisoformat(date_str)
        end = start + timedelta(hours=1)
        yield from self.get_data_stream(start, end, symbol)

    def day_data(self, date_str: str, symbol: Symbol) -> PriceStream:
        start = datetime.fromisoformat(date_str)
        end = start + timedelta(days=1)
        yield from self.get_data_stream(start, end, symbol)

    def week_data(self, date_str: str, symbol: Symbol) -> PriceStream:
        week_dt = datetime.fromisoformat(date_str)
        start = week_dt - timedelta(days=week_dt.weekday())
        end = start + timedelta(days=6)
        yield from self.get_data_stream(start, end, symbol)

    def get_result_set(self, symbol: Symbol, start: datetime, end: datetime, limit=100) -> ResultSet:
        query_str = """
            from(bucket: "tsdata")
              |> range(start: {start}Z, stop: {end}Z)
              |> filter(fn: (r) => r["instrument"] == "{symbol}")
              |> filter(fn: (r) => r["_measurement"] == "price")
              |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        """.format(limit=limit, symbol=symbol.value, start=start.isoformat(), end=end.isoformat())
        return self._query_api.query(query_str)

    def get_data_stream(
            self, start: datetime, end: datetime, symbol: Symbol
    ) -> PriceStream:
        log.info('data from %s till %s', start, end)
        current_start = start
        has_more = True
        while has_more and current_start < end:
            log.debug('getting next chunk %s', current_start)
            results = self.get_result_set(
                symbol, current_start, end, limit=100)
            has_more = False
            # todo: reuse ignorant pagination, so it can be used in the chunking for caching
            log.info('query-result', extra={'r': results})
            for flux_table in results:
                log.info('data-point', extra={'point': flux_table})
                for record in flux_table:
                    log.info('data-point', extra={'dp': record})
                    yield PricePoint(record['_time'], record['ask'], record['bid'])


def get_data_reader() -> DataReader:
    return DataReader(
        config.influx_url,
        config.influx_token,
        config.influx_org
    )
