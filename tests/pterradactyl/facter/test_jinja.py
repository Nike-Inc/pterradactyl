import unittest
import pterradactyl.facter.jinja as jinja


class TestFacterJinjsCommands(unittest.TestCase):

    def test_jinja_facts(self):
        jinja_facter_data = {
            'state_prefix': '{{ deployment }}.tfstate.json'
        }
        output_facts = jinja.JinjaFacter(jinja_facter_data).facts()
        assert output_facts.get('state_prefix') == ".tfstate.json"
