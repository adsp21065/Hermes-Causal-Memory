import unittest

from store import slug


class StoreTests(unittest.TestCase):
    def test_slug_is_stable_and_safe(self):
        self.assertEqual(slug("Capture DUT Trigger!"), "capture-dut-trigger")
        self.assertEqual(slug("___"), "untitled-task")


if __name__ == "__main__":
    unittest.main()
