import unittest
from pterradactyl.commands.state import StateCommand
from mock import patch


class TestEnvCommands(unittest.TestCase):

    def test_env_commands(self):
        with patch('pterradactyl.commands.manifest.ManifestCommand.__init__') as base_mock:
            with patch('pterradactyl.commands.state.ManifestCommand') as manifest_mock:
                base_mock.return_value = None
                expected_subcommands = ["list", "mv", "pull", "push", "rm", "show"]
                command = StateCommand(manifest_mock())
                manifest_mock.assert_called_with()
                self.assertListEqual(command.subcommands, expected_subcommands)
