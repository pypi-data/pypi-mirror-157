#

import os
import unittest

from deployconfigs.djangoconfigs import DjangoDeployConfigs, DEFAULT_EMAIL_ENV

conf = DjangoDeployConfigs(defaults={DEFAULT_EMAIL_ENV: ''})


class EmailTestSuite(unittest.TestCase):
    def test_smtps_parsing(self):
        url = 'smtps://user@domain.com:password@smtp.example.com:587'
        url = conf.parse_email_url(url)

        assert url['EMAIL_BACKEND'] == 'django.core.mail.backends.smtp.EmailBackend'
        assert url['EMAIL_HOST'] == 'smtp.example.com'
        assert url['EMAIL_HOST_PASSWORD'] == 'password'
        assert url['EMAIL_HOST_USER'] == 'user@domain.com'
        assert url['EMAIL_PORT'] == 587
        assert url['EMAIL_USE_TLS'] is True
        assert url['EMAIL_USE_SSL'] is False

    def test_console_parsing(self):
        url = 'console://'
        url = conf.parse_email_url(url)
        assert url['EMAIL_BACKEND'] == 'django.core.mail.backends.console.EmailBackend'
        assert url['EMAIL_HOST'] == ''
        assert url['EMAIL_HOST_PASSWORD'] == ''
        assert url['EMAIL_HOST_USER'] == ''
        assert url['EMAIL_PORT'] == ''
        assert url['EMAIL_USE_TLS'] is False
        assert url['EMAIL_USE_SSL'] is False

    def test_email_url(self):
        os.environ['EMAIL_URL'] = 'smtps://user@domain.com:password@smtp.example.com:587'

        url = conf.email_dict()

        assert url['EMAIL_BACKEND'] == 'django.core.mail.backends.smtp.EmailBackend'
        assert url['EMAIL_HOST'] == 'smtp.example.com'
        assert url['EMAIL_HOST_PASSWORD'] == 'password'
        assert url['EMAIL_HOST_USER'] == 'user@domain.com'
        assert url['EMAIL_PORT'] == 587
        assert url['EMAIL_USE_TLS'] is True
        assert url['EMAIL_USE_SSL'] is False

    def test_smtp_backend_with_ssl(self):
        url = 'smtp://user@domain.com:pass@smtp.example.com:465/?ssl=True'
        url = conf.parse_email_url(url)
        assert url['EMAIL_USE_SSL'] is True
        assert url['EMAIL_USE_TLS'] is False

    def test_smtps_backend_with_ssl(self):
        url = 'smtps://user@domain.com:pass@smtp.example.com:465/?ssl=True'
        url = conf.parse_email_url(url)
        assert url['EMAIL_USE_SSL'] is True
        assert url['EMAIL_USE_TLS'] is False

    def test_smtp_backend_with_tls(self):
        url = 'smtp://user@domain.com:pass@smtp.example.com:587/?tls=True'
        url = conf.parse_email_url(url)
        assert url['EMAIL_USE_SSL'] is False
        assert url['EMAIL_USE_TLS'] is True

    def test_special_chars(self):
        url = 'smtp://user%21%40%23%245678:pass%25%5E%26%2A%28%29123@smtp.example.com:587'
        url = conf.parse_email_url(url)
        assert url['EMAIL_HOST_PASSWORD'] == 'pass%^&*()123'
        assert url['EMAIL_HOST_USER'] == 'user!@#$5678'

    def test_file_path(self):
        url = 'smtp://user@domain.com:pass@smtp.example.com:587//tmp/app-messages?tls=True'
        url = conf.parse_email_url(url)
        assert url['EMAIL_FILE_PATH'] == "/tmp/app-messages"
        assert url['EMAIL_USE_SSL'] is False
        assert url['EMAIL_USE_TLS'] is True

    def test_celery_smtp(self):
        url = 'celery+smtp://user@domain.com:password@smtp.example.com:587'
        url = conf.parse_email_url(url)
        assert url['EMAIL_BACKEND'] == 'djcelery_email.backends.CeleryEmailBackend'
        assert url['EMAIL_HOST'] == 'smtp.example.com'
        assert url['EMAIL_HOST_PASSWORD'] == 'password'
        assert url['EMAIL_HOST_USER'] == 'user@domain.com'
        assert url['EMAIL_PORT'] == 587
        assert url['EMAIL_USE_TLS'] is False
        assert url['EMAIL_USE_SSL'] is False
        assert 'CELERY_EMAIL_TASK_CONFIG' in url

    def test_celery_smtps(self):
        url = 'celery+smtps://user@domain.com:password@smtp.example.com:587?tls=true&queue=email-queue&from=a@b.com'
        url = conf.parse_email_url(url)
        assert url['EMAIL_BACKEND'] == 'djcelery_email.backends.CeleryEmailBackend'
        assert url['EMAIL_HOST'] == 'smtp.example.com'
        assert url['EMAIL_HOST_PASSWORD'] == 'password'
        assert url['EMAIL_HOST_USER'] == 'user@domain.com'
        assert url['EMAIL_PORT'] == 587
        assert url['EMAIL_USE_TLS'] is True
        assert url['EMAIL_USE_SSL'] is False
        assert 'CELERY_EMAIL_TASK_CONFIG' in url

        taskconf = url['CELERY_EMAIL_TASK_CONFIG']
        assert 'tls' not in taskconf
        assert taskconf['queue'] == 'email-queue'

    def test_empty_email_url(self):
        os.environ.pop('EMAIL_URL', None)
        url = conf.email_dict()

        assert url['EMAIL_BACKEND'] is None
        assert url['EMAIL_HOST'] is None
        assert url['EMAIL_HOST_PASSWORD'] is None
        assert url['EMAIL_HOST_USER'] is None
        assert url['EMAIL_PORT'] is None
        assert url['EMAIL_USE_TLS'] is False
        assert url['EMAIL_USE_SSL'] is False


if __name__ == '__main__':
    unittest.main()
