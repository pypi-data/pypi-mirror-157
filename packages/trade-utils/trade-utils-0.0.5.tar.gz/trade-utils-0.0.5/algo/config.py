import logging
import os

import yaml

log = logging.getLogger(__name__)


class Config(object):
    config_data = {}

    @classmethod
    def load_config(cls):
        config_filename = cls._from_env('CONFIG_FILE', '~/config.yml')
        log.info(
            'loading config file',
            extra={'config-filename': config_filename}
        )
        config_data = {}
        try:
            with open(config_filename, 'r', encoding='utf-8') as config_file:
                config_data = yaml.full_load(config_file)
                # todo: add some masking to the security configs
                log.debug('config data', extra={'config-data': config_data})

        except FileNotFoundError:
            log.exception('no config file')
        return config_data

    def __init__(self) -> None:
        self.config_data = self.load_config()

    # todo: remove with next update
    @property
    def influx_host(self):
        return self._from_env('INFLUX_HOST', 'localhost')

    @staticmethod
    def _from_env(name: str, default=None):
        return os.environ.get(name, default)

    @property
    def influx(self):
        return self.config_data.get('influx', {})

    @property
    def influx_token(self):
        return self.influx.get('token')

    @property
    def influx_url(self):
        return self.influx.get('url')

    @property
    def influx_org(self):
        return self.influx.get('org')

    @property
    def oanda(self):
        return self.config_data.get('oanda', {})

    @property
    def oanda_token(self):
        return self.oanda.get('TOKEN')

    @property
    def oanda_stream_host_name(self):
        return self.oanda.get('STREAM_HOST_NAME')

    @property
    def oanda_account_id(self):
        return self.oanda.get('ACCOUNT_ID')


# config = Config()
class LazyConfig():
    def __init__(self) -> None:
        self.config = None

    def __getattr__(self, item):
        if self.config is None:
            self.config = Config()
        return getattr(self.config, item)


config: Config = LazyConfig()
