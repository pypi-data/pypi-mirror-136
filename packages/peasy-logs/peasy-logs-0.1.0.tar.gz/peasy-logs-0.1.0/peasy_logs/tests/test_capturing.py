from unittest import TestCase

from peasy_logs import Capturing


class TestCapture(TestCase):
    def test_capture(self):
        with Capturing() as output:
            print("Hello world!")

        self.assertEqual(output, ["Hello world!"])
