#

import os
import unittest
from pathlib import Path

from deployconfigs import DeployConfigs
from deployconfigs.deployconfigs import ConfigIsRequiredButNotOverridden, DEFAULT_ENV

print(__file__)
BASE_DIR = Path(__file__).resolve().parent


class TestConfigDefaults(unittest.TestCase):
    def test_required(self):
        d = DeployConfigs(defaults={'BB': '1', 'CC': '__REQUIRED__'})

        with self.assertRaises(ConfigIsRequiredButNotOverridden):
            d.get('AA')
        self.assertEqual(d.get_int('AA', default=200), 200)
        self.assertEqual(d.get_int('BB'), 1)
        self.assertEqual(d.get_int('BB', default=2), 1)
        with self.assertRaises(ConfigIsRequiredButNotOverridden):
            d.get_int('CC')
        with self.assertRaises(ConfigIsRequiredButNotOverridden):
            d.get_int('CC', default=3)

    def test_get_bool(self):
        d = DeployConfigs(defaults={'BB': '1'})
        with self.assertRaises(ValueError):
            d.get_bool('AA', 'string')
        with self.assertRaises(ValueError):
            d.get_bool('AA', None)
        with self.assertRaises(ValueError):
            d.get_bool('AA', 10)
        self.assertEqual(d.get_bool('AA', True), True)

    def test_ini_file(self):
        # default file not found
        with self.assertRaises(FileNotFoundError):
            DeployConfigs(default_conf_file=BASE_DIR / 'not-found')

        # default exists, but extra not found (no explicit extra)
        d = DeployConfigs(default_conf_file=BASE_DIR / 'test-1.ini',
                          extra_conf_file=BASE_DIR / 'not-found')
        self.assertEqual(d.get_int('INT_VAL'), 100)
        with self.assertRaises(ConfigIsRequiredButNotOverridden):
            d.get('REQ')

        # default exists, no extra file defined, but explicit extra not found
        os.environ[DEFAULT_ENV] = 'config2.ini'
        with self.assertRaises(FileNotFoundError):
            DeployConfigs(default_conf_file=BASE_DIR / 'test-1.ini')

        # default exists, extra file exists, but explicit extra not found
        with self.assertRaises(FileNotFoundError):
            DeployConfigs(default_conf_file=BASE_DIR / 'test-1.ini',
                          extra_conf_file=BASE_DIR / 'test-2.ini')

        # default exists, extra file not exists, explicit config exists
        os.environ[DEFAULT_ENV] = str(BASE_DIR / 'test-2.ini')
        d = DeployConfigs(default_conf_file=BASE_DIR / 'test-1.ini',
                          extra_conf_file=BASE_DIR / 'not-found')
        self.assertEqual(d.get_int('INT_VAL'), 200)
        with self.assertRaises(ConfigIsRequiredButNotOverridden):
            d.get('REQ')
        self.assertEqual(d.get('AA'), 'test')

        # default exists, extra file not defined, explicit config exists
        d = DeployConfigs(default_conf_file=BASE_DIR / 'test-1.ini')
        self.assertEqual(d.get_int('INT_VAL'), 200)
        self.assertEqual(d.get('AA'), 'test')

        os.environ.pop(DEFAULT_ENV)
        d = DeployConfigs(default_conf_file=BASE_DIR / 'test-1.ini',
                          extra_conf_file=BASE_DIR / 'test-2.ini')
        self.assertEqual(d.get_int('INT_VAL'), 200)
        with self.assertRaises(ConfigIsRequiredButNotOverridden):
            d.get('REQ')
        self.assertEqual(d.get('AA'), 'test')
