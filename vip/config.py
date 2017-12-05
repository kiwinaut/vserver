import argparse
import os

HOME = os.environ['HOME']

class ConfigManager(object):
    "Config manager"

    def __init__(self):
        self.defaults = {
            'database.path': '%s/.cache/vip.db' % HOME,
        }
        self.config = {}
        self.options = {}
        # self.arguments = []

    def parse(self):
        parser = argparse.ArgumentParser(description='vip server', prog='vip')
        parser.add_argument('--test', action="store_true", help="Use Test Files")

        args = parser.parse_args()
        self.options['dev'] = args.test
        if args.test:
            self.options['database.path'] = ':memory:'


    def __setitem__(self, key, value, config=True):
        self.options[key] = value
        if config:
            self.config[key] = value

    def __getitem__(self, key):
        return self.options.get(key, self.config.get(key,
            self.defaults.get(key)))


CONFIG = ConfigManager()