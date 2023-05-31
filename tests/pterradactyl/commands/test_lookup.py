import argparse
import os
import unittest
from unittest.mock import patch

import pytest

from pterradactyl.commands.lookup import LookupCommand


class TestLookupCommands(unittest.TestCase):

    def setUp(self) -> None:
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config = os.path.join(os.getcwd(), 'tests/resources/config/pterra.yaml')
        self.facts = os.path.join(os.getcwd(), 'tests/resources/config/facts.yaml')
        self.facts_invalid = os.path.join(os.getcwd(), 'tests/resources/config/facts_invalid.yaml')
        self.parser = self.create_parser()

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--test', '-t')
        return parser

    def test_parser_args(self):
        with patch('os.getcwd') as cwd_mock:
            cwd_mock.return_value = self.config
            self.lc = LookupCommand(config=self.config, parser=self.parser)
            parsed = self.parser.parse_args((['--backend', 'yaml', '--facts', self.facts, '--set', 'foo=bar', '--set', 'foo1=bar1']))
            self.assertEqual(parsed.backend, 'yaml')
            self.assertEqual(parsed.set, ['foo=bar', 'foo1=bar1'])
            self.assertEqual(parsed.facts, self.facts)
            self.lc.execute(parsed, ['hierarchy'])

    def test_lookup_should_exit_with_invalid_yaml_file(self):
        with patch('os.getcwd') as cwd_mock_exception:
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                cwd_mock_exception.return_value = self.config
                self.lc = LookupCommand(config=self.config, parser=self.parser)
                parsed = self.parser.parse_args((['--backend', 'yaml', '--facts', self.facts_invalid, '--set', 'foo=bar', '--set', 'foo1=bar1']))
                self.lc.execute(parsed, ['hierarchy'])
                assert pytest_wrapped_e.type == SystemExit
                assert pytest_wrapped_e.value.code == 42

    def test_lookup_invalid_set_facts(self):
        with patch('os.getcwd') as cwd_mock_exception:
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                cwd_mock_exception.return_value = self.config
                self.lc = LookupCommand(config=self.config, parser=self.parser)
                parsed = self.parser.parse_args((['--backend', 'yaml', '--facts', self.facts, '--set', 'foo=bar', '--set', 'foo:bar']))
                self.lc.execute(parsed, ['hierarchy'])
                assert pytest_wrapped_e.type == SystemExit
                assert pytest_wrapped_e.value.code == 42
