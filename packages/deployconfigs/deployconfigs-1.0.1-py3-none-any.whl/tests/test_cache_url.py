#

import os
import unittest

from deployconfigs import DeployConfigs
from deployconfigs.djangoconfigs import DjangoDeployConfigs, DEFAULT_CACHE_ENV

conf = DjangoDeployConfigs(defaults={DEFAULT_CACHE_ENV: '', 'HERP': ''})


class TestConfigOptions(unittest.TestCase):
    backend = 'django.core.cache.backends.memcached.PyLibMCCache'

    def test_setting_default_var(self):
        config = conf.cache_dict(default='memcached://127.0.0.1:11211')
        assert config['BACKEND'] == self.backend
        assert config['LOCATION'] == '127.0.0.1:11211'

    def test_setting_env_var_name(self):
        os.environ['HERP'] = 'memcached://127.0.0.1:11211'
        config = conf.cache_dict('HERP')
        assert config['BACKEND'] == self.backend
        assert config['LOCATION'] == '127.0.0.1:11211'

    def test_setting_env_var(self):
        os.environ['CACHE_URL'] = 'redis://127.0.0.1:6379/0?key_prefix=site1'
        config = conf.cache_dict()

        assert config['BACKEND'] == 'django_redis.cache.RedisCache'
        assert config['LOCATION'] == 'redis://127.0.0.1:6379/0'


class TestCore(unittest.TestCase):
    def test_config_defaults_to_locmem(self):
        if os.environ.get('CACHE_URL'):
            del os.environ['CACHE_URL']
        config = conf.cache_dict()
        assert config['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'

    def test_db_url_returns_database_cache_backend(self):
        url = 'db://super_caching_table'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'django.core.cache.backends.db.DatabaseCache'
        assert config['LOCATION'] == 'super_caching_table'

    def test_dummy_url_returns_dummy_cache(self):
        config = conf.parse_cache_url('dummy://')
        assert config['BACKEND'] == 'django.core.cache.backends.dummy.DummyCache'

    def test_file_url_returns_file_cache_backend(self):
        config = conf.parse_cache_url('file:///herp')
        assert config['BACKEND'] == 'django.core.cache.backends.filebased.FileBasedCache'
        assert config['LOCATION'] == '/herp'

    def test_locmem_url_returns_locmem_cache(self):
        config = conf.parse_cache_url('locmem://')
        assert config['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'

    def test_query_string_params_are_converted_to_cache_arguments(self):
        url = 'redis:///path/to/socket?key_prefix=foo&bar=herp'
        config = conf.parse_cache_url(url)

        assert config['KEY_PREFIX'] == 'foo'
        assert config['BAR'] == 'herp'

    def test_query_string_params_are_converted_to_cache_options(self):
        url = 'db://my_cache_table?max_entries=1000&cull_frequency=2'
        config = conf.parse_cache_url(url)

        assert 'OPTIONS' in config
        assert config['OPTIONS']['MAX_ENTRIES'] == 1000
        assert config['OPTIONS']['CULL_FREQUENCY'] == 2

    def test_unknown_cache_backend(self):
        with self.assertRaises(Exception):
            conf.parse_cache_url('donkey://127.0.0.1/foo')


class TestMemCached(unittest.TestCase):
    def test_memcached_url_returns_pylibmc_cache(self):
        url = 'memcached://127.0.0.1:11211?key_prefix=site1'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'django.core.cache.backends.memcached.PyLibMCCache'
        assert config['LOCATION'] == '127.0.0.1:11211'
        assert config['KEY_PREFIX'] == 'site1'

    def test_memcached_url_multiple_locations(self):
        url = 'memcached://127.0.0.1:11211,192.168.0.100:11211?key_prefix=site1'
        config = conf.parse_cache_url(url)
        assert config['LOCATION'] == '127.0.0.1:11211;192.168.0.100:11211'

    def test_memcached_socket_url(self):
        url = 'memcached:///path/to/socket/'
        config = conf.parse_cache_url(url)
        assert config['LOCATION'] == 'unix:/path/to/socket/'


class TestRedis(unittest.TestCase):
    def test_hiredis(self):
        url = 'hiredis://127.0.0.1:6379/0?key_prefix=site1'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'django_redis.cache.RedisCache'
        assert config['LOCATION'] == 'redis://127.0.0.1:6379/0'
        assert config['OPTIONS']['PARSER_CLASS'] == 'redis.connection.HiredisParser'

    def test_hiredis_socket(self):
        url = 'hiredis:///path/to/socket/1?key_prefix=site1'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'django_redis.cache.RedisCache'
        assert config['LOCATION'] == 'unix:/path/to/socket:1'
        assert config['OPTIONS']['PARSER_CLASS'] == 'redis.connection.HiredisParser'

    def test_redis(self):
        url = 'redis://127.0.0.1:6379/0?key_prefix=site1'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'django_redis.cache.RedisCache'
        assert config['LOCATION'] == 'redis://127.0.0.1:6379/0'

    def test_redis_socket(self):
        url = 'redis:///path/to/socket/1?key_prefix=site1'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'django_redis.cache.RedisCache'
        assert config['LOCATION'] == 'unix:/path/to/socket:1'
        assert 'OPTIONS' not in config

    def test_redis_with_password(self):
        url = 'redis://:redispass@127.0.0.1:6379/0'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'django_redis.cache.RedisCache'
        assert config['LOCATION'] == 'redis://127.0.0.1:6379/0'
        assert config['OPTIONS']['PASSWORD'] == 'redispass'


class TestUwsgiCache(unittest.TestCase):
    def test_uwsgicache_url_returns_uwsgicache_cache(self):
        url = 'uwsgicache://cachename/'
        config = conf.parse_cache_url(url)

        assert config['BACKEND'] == 'uwsgicache.UWSGICache'
        assert config['LOCATION'] == 'cachename'

    def test_uwsgicache_default_location(self):
        url = 'uwsgicache://'
        config = conf.parse_cache_url(url)
        assert config['LOCATION'] == 'default'


if __name__ == '__main__':
    unittest.main()
