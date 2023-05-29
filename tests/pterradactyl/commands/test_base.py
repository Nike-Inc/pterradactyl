import unittest

from pterradactyl.commands.base import AbstractBaseCommand


class TestBaseCommands(unittest.TestCase):

    def setUp(self) -> None:
        self.config = {}
        self.parser = None
        self.command = AbstractBaseCommand(self.config, self.parser)

    def test_argument(self):
        argument = self.command.argument(foo="bar")
        self.assertIsNone(argument)

    def test_command_name(self):
        command_name = self.command.command_name()
        self.assertIsNone(command_name)

    def test_execute(self):
        execute = self.command.execute(["foo", "bar"], ["foo1", "bar1"])
        self.assertIsNone(execute)
