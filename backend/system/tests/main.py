from django.test import TestCase
from django.utils.timezone import now


class MainTestCase(TestCase):
    def setUp(self):
        pass

    def test_that_tests_work(self):
        self.assertEqual(100, 10+90)

