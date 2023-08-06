#

import os
import unittest

from deployconfigs.djangoconfigs import DjangoDeployConfigs, DEFAULT_DATABASE_ENV

conf = DjangoDeployConfigs(defaults={DEFAULT_DATABASE_ENV: ''})


class DatabaseTestSuite(unittest.TestCase):
    def test_postgres_parsing(self):
        url = 'postgres://user00name:pass11word@a.b.example.com:5431/dummypath'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.postgresql'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431

    def test_postgres_unix_socket_parsing(self):
        url = 'postgres://%2Fvar%2Frun%2Fpostgresql/dummypath'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.postgresql'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == '/var/run/postgresql'
        assert url['USER'] == ''
        assert url['PASSWORD'] == ''
        assert url['PORT'] == ''

        url = 'postgres://%2FUsers%2Fpostgres%2FRuN/dummypath'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.postgresql'
        assert url['HOST'] == '/Users/postgres/RuN'
        assert url['USER'] == ''
        assert url['PASSWORD'] == ''
        assert url['PORT'] == ''

    def test_postgres_search_path_parsing(self):
        url = 'postgres://user00name:pass11word@a.b.example.com:5431/dummypath?currentSchema=otherschema'
        url = conf.parse_database_url(url)
        assert url['ENGINE'] == 'django.db.backends.postgresql'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431
        assert url['OPTIONS']['options'] == '-c search_path=otherschema'
        assert 'currentSchema' not in url['OPTIONS']

    def test_postgres_parsing_with_special_characters(self):
        url = 'postgres://%23user:%23password@a.b.example.com:5431/%23database'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.postgresql'
        assert url['NAME'] == '#database'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == '#user'
        assert url['PASSWORD'] == '#password'
        assert url['PORT'] == 5431

    def test_postgis_parsing(self):
        url = 'postgis://user00name:pass11word@a.b.example.com:5431/dummypath'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.contrib.gis.db.backends.postgis'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431

    def test_postgis_search_path_parsing(self):
        url = 'postgis://user00name:pass11word@a.b.example.com:5431/dummypath?currentSchema=otherschema'
        url = conf.parse_database_url(url)
        assert url['ENGINE'] == 'django.contrib.gis.db.backends.postgis'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431
        assert url['OPTIONS']['options'] == '-c search_path=otherschema'
        assert 'currentSchema' not in url['OPTIONS']

    def test_mysql_gis_parsing(self):
        url = 'mysqlgis://user00name:pass11word@a.b.example.com:5431/dummypath'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.contrib.gis.db.backends.mysql'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431

    def test_mysql_connector_parsing(self):
        url = 'mysql-connector://user00name:pass11word@a.b.example.com:5431/dummypath'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'mysql.connector.django'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431

    def test_cleardb_parsing(self):
        url = 'mysql://user00name:pass11word@a.b.example.com/dymmypath?reconnect=true'
        url = conf.parse_database_url(url)
        assert url['ENGINE'] == 'django.db.backends.mysql'
        assert url['NAME'] == 'dymmypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == ''

    def test_database_url_with_default(self):
        os.environ.pop('DATABASE_URL', None)
        conf2 = DjangoDeployConfigs(defaults={DEFAULT_DATABASE_ENV: 'sqlite:///db.sqlite3'})
        url = conf2.database_dict()
        print(url)
        assert url['ENGINE'] == 'django.db.backends.sqlite3'
        assert url['NAME'] == 'db.sqlite3'
        assert not url.get('HOST', None)

    def test_database_url(self):
        os.environ.pop('DATABASE_URL', None)
        a = conf.database_dict()
        assert not a

        os.environ['DATABASE_URL'] = \
            'postgres://user00name:pass11word@a.b.example.com:5431/dummypath'

        url = conf.database_dict()

        assert url['ENGINE'] == 'django.db.backends.postgresql'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431

    def test_empty_sqlite_url(self):
        url = 'sqlite://'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.sqlite3'
        assert url['NAME'] == ':memory:'

    def test_memory_sqlite_url(self):
        url = 'sqlite://:memory:'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.sqlite3'
        assert url['NAME'] == ':memory:'

    def test_parse_engine_setting(self):
        engine = 'django_mysqlpool.backends.mysqlpool'
        url = 'mysql://user00name:pass11word@a.b.example.com/dymmypath?reconnect=true'
        url = conf.parse_database_url(url, engine)

        assert url['ENGINE'] == engine

    def test_config_engine_setting(self):
        engine = 'django_mysqlpool.backends.mysqlpool'
        os.environ['DATABASE_URL'] = \
            'mysql://user00name:pass11word@a.b.example.com/dymmypath?reconnect=true'
        url = conf.database_dict(engine=engine)

        assert url['ENGINE'] == engine

    def test_parse_conn_max_age_setting(self):
        conn_max_age = 600
        url = 'mysql://user00name:pass11word@a.b.example.com/dymmypath?reconnect=true&conn_max_age=%s' % conn_max_age
        url = conf.parse_database_url(url)

        assert url['CONN_MAX_AGE'] == conn_max_age

    def test_config_conn_max_age_setting(self):
        conn_max_age = 600
        os.environ['DATABASE_URL'] = \
            'mysql://user00name:pass11word@a.b.example.com/dymmypath?reconnect=true&conn_max_age=%s' % conn_max_age
        url = conf.database_dict()

        assert url['CONN_MAX_AGE'] == conn_max_age

    def test_database_url_with_options(self):
        # Test full options
        os.environ['DATABASE_URL'] = \
            'postgres://user00name:pass11word@a.b.example.com:5431/dummypath' \
            '?sslrootcert=rds-combined-ca-bundle.pem&sslmode=verify-full'
        url = conf.database_dict()

        assert url['ENGINE'] == 'django.db.backends.postgresql'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5431
        assert url['OPTIONS'] == {
            'sslrootcert': 'rds-combined-ca-bundle.pem',
            'sslmode': 'verify-full'
        }

        # Test empty options
        os.environ['DATABASE_URL'] = \
            'postgres://user00name:pass11word@a.b.example.com:5431/dummypath?'
        url = conf.database_dict()
        assert 'OPTIONS' not in url

    def test_mysql_database_url_with_sslca_options(self):
        os.environ['DATABASE_URL'] = \
            'mysql://user00name:pass11word@a.b.example.com:3306/dummypath?ssl-ca=rds-combined-ca-bundle.pem'
        url = conf.database_dict()

        assert url['ENGINE'] == 'django.db.backends.mysql'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 3306
        assert url['OPTIONS'] == {
            'ssl': {
                'ca': 'rds-combined-ca-bundle.pem'
            }
        }

        # Test empty options
        os.environ['DATABASE_URL'] = \
            'mysql://user00name:pass11word@a.b.example.com:3306/dummypath?'
        url = conf.database_dict()
        assert 'OPTIONS' not in url

    def test_oracle_parsing(self):
        url = 'oracle://user00name:pass11word@a.b.example.com:1521/hr'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.oracle'
        assert url['NAME'] == 'hr'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 1521

    def test_oracle_gis_parsing(self):
        url = 'oraclegis://user00name:pass11word@a.b.example.com:1521/hr'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.contrib.gis.db.backends.oracle'
        assert url['NAME'] == 'hr'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 1521

    def test_oracle_dsn_parsing(self):
        url = (
            'oracle://user00name:pass11word@/'
            '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)'
            '(HOST=a.b.example.com)(PORT=1521)))'
            '(CONNECT_DATA=(SID=hr)))'
        )
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.oracle'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['HOST'] == ''
        assert url['PORT'] == ''

        dsn = (
            '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)'
            '(HOST=a.b.example.com)(PORT=1521)))'
            '(CONNECT_DATA=(SID=hr)))'
        )

        assert url['NAME'] == dsn

    def test_oracle_tns_parsing(self):
        url = 'oracle://user00name:pass11word@/tnsname'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django.db.backends.oracle'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['NAME'] == 'tnsname'
        assert url['HOST'] == ''
        assert url['PORT'] == ''

    def test_redshift_parsing(self):
        url = 'redshift://user00name:pass11word@a.b.example.com:5439/dummypath?currentSchema=otherschema'
        url = conf.parse_database_url(url)

        assert url['ENGINE'] == 'django_redshift_backend'
        assert url['NAME'] == 'dummypath'
        assert url['HOST'] == 'a.b.example.com'
        assert url['USER'] == 'user00name'
        assert url['PASSWORD'] == 'pass11word'
        assert url['PORT'] == 5439
        assert url['OPTIONS']['options'] == '-c search_path=otherschema'
        assert 'currentSchema' not in url['OPTIONS']


if __name__ == '__main__':
    unittest.main()
