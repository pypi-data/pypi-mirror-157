# This file is placed in the Public Domain.


"composition tests"


import unittest


from genocide.mbx import Email


class Test_Mbx(unittest.TestCase):

    def test_mail(self):
        e = Email()        
        self.assertEqual(type(e), Email)
