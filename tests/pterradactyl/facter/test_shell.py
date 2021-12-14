import unittest
import pterradactyl.facter.shell as shell


class TestFacterShellCommands(unittest.TestCase):

    def test_jsonpath(self):
        data = '{"hello":["world1", "world2"] }'
        path = "$.hello[0]"
        expected = "world1"
        actual = shell.jsonpath(data, path)
        assert actual == expected

    def test_jsonpath_zero_match(self):
        data = '{}'
        path = "$.hello[0]"
        actual = shell.jsonpath(data, path)
        assert actual is None

    def test_jsonpath_multiple_match(self):
        data = '{"hello":["world1", "world2"] }'
        path = "$.hello[*]"
        expected = ["world1", "world2"]
        actual = shell.jsonpath(data, path)
        assert actual == expected

    def test_shell_facts(self):
        shell_facter_data = {
            'single_command': 'echo \'single_command\'',
            'json_parse_command_output': {
                'command': 'echo \'{"hello":["world1", "world2"] }\'',
                'jsonpath': '$.hello[0]',
                'data_json': '{"hello":["world1", "world2"] }'
            }
        }
        output_facts = shell.ShellFacter(shell_facter_data).facts()
        assert output_facts.get('single_command') == "single_command"
        assert output_facts.get('json_parse_command_output') == "world1"
