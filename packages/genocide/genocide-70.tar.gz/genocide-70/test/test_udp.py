# This file is placed in the Public Domain.


"udp tests"


import unittest


from genocide.udp import UDP



class Test_UDP(unittest.TestCase):

    def test_udp(self):
        u = UDP()
        self.assertEqual(type(u), UDP)
