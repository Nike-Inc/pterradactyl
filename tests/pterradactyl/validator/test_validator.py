import unittest
from unittest.mock import patch

from pterradactyl.validator import Validator
from pterradactyl.validator.base import BaseValidator


class TestValidator(unittest.TestCase):

    def test_base_validator(self):
        with patch('pterradactyl.validator.base.BaseValidator.__init__') as mock_init:
            mock_init.return_value = None
            bv = BaseValidator(mock_init())
            self.assertTrue(bv.validate())

    def test_validator(self):
        facts = {
            'state_prefix': 'ut-test0-na-uswest2.tfstate.json'
        }
        v = Validator('.', facts)
        self.assertTrue(v.validate())
