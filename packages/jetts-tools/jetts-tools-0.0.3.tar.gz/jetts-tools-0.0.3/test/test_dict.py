from src.jettools import dict
import unittest


class TestGetNestedKey(unittest.TestCase):
    def test_should_return_none_if_no_keys(self):
        d = {'level1': {'level1': 2}}
        self.assertEqual(dict.get(d, []), None)

    def test_should_grab_val_if_just_string(self):
        d = {'level1': 3}
        self.assertEqual(dict.get(d, 'level1'), 3)

    def test_should_get_nested_value_if_exists(self):
        d = {'level1': {'level2': 2}}
        self.assertEqual(dict.get(d, ['level1', 'level2']), 2)

    def test_should_return_none_if_fake_levels(self):
        d = {'level1': {'level2': 2}}
        self.assertEqual(dict.get(d, ['level2', 'level3']), None)
