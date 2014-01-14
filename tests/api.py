import unittest

import livefyre


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        token = 'thisisanawesometoken'
        self.lf = livefyre.Livefyre()

    def test_register_profile_pull_interface(self):
        resp = self.lf.register_profile_pull_interface(
            url='http://www.domain.com/profile/?id={id}')

        expected = {
            'url': 'http://dailydot-0.fyre.co/?pull_profile_url=http%3A%2F%2Fwww.domain.com%2Fprofile%2F%3Fid%3D%7Bid%7D&actor_token=thisisanawesometoken',
            'body': None,
        }

        self.assertEqual(resp.url, expected['url'])
        self.assertEqual(resp.request.body, expected['body'])

        print resp.content
        print resp.url

        self.assertEqual(resp.status_code, 204)

    def test_ping_to_pull(self):
        resp = self.lf.ping_to_pull('bob_the_builder')

        expected = {
            'url': 'http://dailydot-0.fyre.co/api/v3_0/user/bob_the_builder/refresh',
            'body': 'lftoken=thisisanawesometoken',
        }

        self.assertEqual(resp.url, expected['url'])
        self.assertEqual(resp.request.body, expected['body'])

        print resp.content
        print resp.url
        self.assertEqual(resp.status_code, 204)

