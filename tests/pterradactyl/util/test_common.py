import unittest

from pterradactyl.util import as_list, lookup, memoize, merge_dict


class TestCommonUtil(unittest.TestCase):

    def memoize_func(self, *arg, **kwargs):
        pass

    def test_as_list_string(self):
        elem = "3"
        r = as_list(elem)
        self.assertListEqual(r, list(elem))

    def test_as_list_list(self):
        elem = ["list_elem"]
        r = as_list(elem)
        self.assertListEqual(r, elem)

    def test_merge_dict(self):
        dict1 = {'a': 'b'}
        dict2 = {'c': 'd'}
        merged_dict = merge_dict(dict1, dict2)
        self.assertDictEqual(merged_dict, {'a': 'b', 'c': 'd'})

    def test_lookup(self):
        data = {'foo': 'bar', 'foo1': 'bar1'}
        value = lookup(data, 'foo')
        self.assertEqual(value, 'bar')

    def test_lookup_with_non_existing_key(self):
        data = {'foo': 'bar', 'foo1': 'bar1'}
        value = lookup(data, 'foo_1')
        self.assertEqual(value, None)

    def test_lookup_should_return_default(self):
        data = {'foo': 'bar', 'foo1': 'bar1'}
        value = lookup(data, 'foo_1', default='bar2')
        self.assertEqual(value, 'bar2')

    def test_memoize(self):
        m = memoize(self.memoize_func(mylist=[1, 2, 3, 4, 5]))
        self.assertTrue(m)
