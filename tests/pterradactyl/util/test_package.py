import unittest
from pterradactyl.util.package import entry_points


class TestPackageUtil(unittest.TestCase):

    def test_entry_points(self):
        expected_entry_points_names = ['arguments', 'environment', 'jinja', 'regex', 'shell']
        ep = entry_points('pterradactyl.facters')
        self.assertListEqual(list(ep.keys()), expected_entry_points_names)
