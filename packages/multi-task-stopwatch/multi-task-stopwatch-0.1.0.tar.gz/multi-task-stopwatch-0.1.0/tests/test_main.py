import time
import unittest

from stopwatch.stopwatch import StopWatch


class TestDropZeroPattern(unittest.TestCase):
    def test_stop_watch(self):
        sw = StopWatch("title")

        sw.start("eat")
        time.sleep(0.12)
        sw.stop()

        sw.start("sleep")
        time.sleep(0.60)
        sw.stop()

        sw.start("work")
        time.sleep(0.35)
        sw.stop()

        print(sw.pretty_print())
