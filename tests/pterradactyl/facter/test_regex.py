import unittest

import pterradactyl.facter.regex as regex


class TestFacterRegexCommands(unittest.TestCase):

    def test_regex_facts(self):
        regex_facter_data = {
            'source': 'deployment',
            'expression': '(?P<family>\w)(?P<account_type>\w)-(?P<product>[a-z]+)(?P<n>\d+)-(?P<serving_region>\w+)-(?P<region>\w+)',
            'transforms': [
                {
                    'region': '{{ region[0:2] }}-{{region[2:-1]}}-{{region[-1]}}'
                }
            ]
        }

        output_facts = regex.RegexFacter(regex_facter_data).facts(facts={'deployment': "ct-test0-na-uswest2"})
        assert output_facts.get('family') == "c"
        assert output_facts.get('account_type') == "t"
        assert output_facts.get('product') == "test"
        assert output_facts.get('n') == "0"
        assert output_facts.get('serving_region') == "na"
        assert output_facts.get('region') == "us-west-2"
