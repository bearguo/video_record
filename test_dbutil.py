import unittest
import dbutil

class DBUtilTest(unittest.TestCase):

    channel_id = "CCTV1"
    def test_get_channel_info(self):
        result = dbutil.get_channel_info('CCTV1')
        dic ={'start': 0, 'sort': 0, 'rtmp_url': 'http://localhost/CCTV1.m3u8', 'client_ip': 'localhost:8080',
             'PID': None, 'channel_name': 'CCTV1', 'channel_id': 'CCTV1', 'id': 1, 'PGID': None, 'active': 0}

        self.assertDictEqual(result,dic)

    def test_get_live_url(self):
        str = dbutil.get_channel_info(self.channel_id)['rtmp_url']
        self.assertEqual(str, "http://localhost/CCTV1.m3u8")

    def test_get_udp_port(self):
        port_int = dbutil.get_udp_port(self.channel_id)
        self.assertEqual(port_int, 8080)

    def test_is_start(self):
        is_start = dbutil.is_start(self.channel_id)
        self.assertEqual(is_start, False)

    def test_set_start(self):
        dbutil.set_start(self.channel_id, True)
        is_start = dbutil.is_start(self.channel_id)
        self.assertEqual(is_start, True)

        dbutil.set_start(self.channel_id, False)
        is_start = dbutil.is_start(self.channel_id)
        self.assertEqual(is_start, False)


if __name__ == '__main__':
    unittest.main()