# This file is placed in the Public Domain.


"event tests"


import unittest


from genocide.evt import Event



class Test_Event(unittest.TestCase):

    def test_event(self):
        e = Event()
        self.assertEqual(type(e), Event)
