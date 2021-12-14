import unittest
from pterradactyl.facter.base import BaseFacter
from pterradactyl.facter import Facter


class TestFacterShellCommands(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {}
        self.command = BaseFacter(self.config)
        self.f = Facter()

    def test_base_facter(self):
        bf = BaseFacter(self.config)
        self.assertIsNone(bf.parser_setup(self.config))
        self.assertEqual(bf.facts(self.config), {})

    def test_to_dict(self):
        todict_obj = self.f.to_dict()
        self.assertTrue(todict_obj)



