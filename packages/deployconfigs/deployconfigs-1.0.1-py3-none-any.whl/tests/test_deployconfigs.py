#

import os
import unittest

from deployconfigs import DeployConfigs
from deployconfigs.deployconfigs import UrlParseResult
from deployconfigs.djangoconfigs import DjangoDeployConfigs, DEFAULT_CACHE_ENV

conf = DjangoDeployConfigs(defaults={DEFAULT_CACHE_ENV: '', 'GENERAL_ENV': ''})


class TestDeployConfigs(unittest.TestCase):
    def test_init(self):
        conf2 = DeployConfigs(defaults={}, configure=False)
        self.assertFalse(conf2.ready)

    def test_parse_shortcut(self):
        url = 'sqlite://:memory:'
        url = conf.parse_database_url(url)

        self.assertEqual(url['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(url['NAME'], ':memory:')

    def test_parse_empty_sqlite_url(self):
        url = 'sqlite://'
        url = conf.parse_database_url(url)

        self.assertEqual(url['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(url['NAME'], ':memory:')

    def test_parse_cache_var(self):
        url = 'memcached://127.0.0.1:11211'
        url = conf.parse_cache_url(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.memcached.PyLibMCCache')
        self.assertEqual(url['LOCATION'], '127.0.0.1:11211')

    def test_parse_email(self):
        url = 'console://'
        url = conf.parse_email_url(url)
        self.assertEqual(url['EMAIL_BACKEND'], 'django.core.mail.backends.console.EmailBackend')

    def test_parse_storage(self):
        url = 's3://'
        url = conf.parse_storage_url(url)
        self.assertEqual(url['scheme'], 's3')

    def test_parse_unknown(self):
        url = 'unknown://'
        with self.assertRaises(RuntimeError):
            url = conf.parse_storage_url(url)
        with self.assertRaises(RuntimeError):
            url = conf.parse_database_url(url)
        with self.assertRaises(RuntimeError):
            url = conf.parse_email_url(url)
        with self.assertRaises(RuntimeError):
            url = conf.parse_cache_url(url)

    def test_result_subclass(self):
        result = UrlParseResult()
        self.assertTrue(result.is_empty())
        self.assertEqual(result.__dict__, {'query_dict': {}})

        result.backend = 'backend'
        self.assertFalse(result.is_empty())

    def test_general_env(self):
        os.environ['GENERAL_ENV'] = 's3://ACCESS-KEY:SECRET-KEY@127.0.0.1:9000/path'
        url = conf.general_dict('GENERAL_ENV')
        self.assertEqual(url['scheme'], 's3')
