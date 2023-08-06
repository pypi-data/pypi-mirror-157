#

import unittest

from deployconfigs.djangoconfigs import DjangoDeployConfigs

conf = DjangoDeployConfigs(defaults={})


class TestDeployConfigs(unittest.TestCase):
    def test_local_windows_not_encoded(self):
        url = 'local:///c:/data/'
        url = conf.parse_storage_url(url)

        self.assertEqual(url['backend'], 'django.core.files.storage.FileSystemStorage')
        self.assertEqual(url['netloc'], '')
        self.assertEqual(url['path'], 'c:/data/')

    def test_wrong_local(self):
        url = 'local://c:/data/'
        with self.assertRaises(AssertionError):
            url = conf.parse_storage_url(url)


if __name__ == '__main__':
    unittest.main()
