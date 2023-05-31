import argparse
import unittest
from unittest.mock import patch

import pterradactyl.facter.arguments as arguments


class TestFacterArguments(unittest.TestCase):

    def test_argument_facts(self):
        argument_facter_data = {
            'deployment': {
                'positional': True,
                'description': 'Deployment ID'
            },
            'stage': {
                'alias': 's',
                'description': 'Stage name (test, dev, stage, prod)'
            },
            'product': {
                'alias': 'p',
                'description': 'Product name (dds, fulfillment, allocation, ...)'
            }
        }

        with patch('pterradactyl.facter.arguments.ArgumentFactActionFactory', autospec=True):
            argument = arguments.ArgumentsFacter(argument_facter_data)
            argument.parser_setup(parser=argparse.ArgumentParser())
            output_facts = argument.facts()

            assert output_facts.get('deployment').value
            assert (output_facts.get('stage'))
            assert (output_facts.get('product'))
