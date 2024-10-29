from .algo import UptimeEstimator
from datetime import time
from unittest import TestCase

class TestUptimeEstimator(TestCase):

    def test_onlydown(self):
        ue = UptimeEstimator()
        ue.add(time(12, 0, 0), False)
        self.assertEqual(0, ue.uptime())
        ue.add(time(13, 0, 0), False)
        self.assertEqual(0, ue.uptime())

    def test_onlyup(self):
        ue = UptimeEstimator()
        ue.add(time(12, 0, 0), True)
        self.assertEqual(100, ue.uptime())
        ue.add(time(13, 0, 0), True)
        self.assertEqual(100, ue.uptime())

    def test_skewdown(self):
        ue = UptimeEstimator()
        ue.add(time(12, 0, 0), True)
        ue.add(time(18, 0, 0), False)
        self.assertEqual(50, ue.uptime())
        ue.add(time(21, 0, 0), False)
        self.assertEqual(43.75, ue.uptime())

    def test_skewup(self):
        ue = UptimeEstimator()
        ue.add(time(12, 0, 0), True)
        ue.add(time(18, 0, 0), False)
        self.assertEqual(50, ue.uptime())
        ue.add(time(21, 0, 0), True)
        self.assertEqual(81.25, ue.uptime())
