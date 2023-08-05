#
# File:    ./tests/unit/test_data.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2022-06-28 12:39:49 +0200
# Project: vutils-python: Python language tools
#
# SPDX-License-Identifier: MIT
#
"""Test `vutils.python.data` module."""

from vutils.testing.testcase import TestCase
from vutils.testing.utils import make_type

from vutils.python.data import merge_data


class MergeDataTestCase(TestCase):
    """Test case for `merge_data`."""

    __slots__ = ()

    def test_merge_lists(self):
        """Test merging two lists."""
        src = [1, 2, "a"]
        dest = [1, "b"]

        merge_data(dest, src)
        self.assertEqual(dest, [1, "b", 1, 2, "a"])

    def test_merge_sets(self):
        """Test merging two sets."""
        src = {1, 2, 3}
        dest = {2, "a"}

        merge_data(dest, src)
        self.assertEqual(dest, {1, 2, 3, "a"})

    def test_merge_dicts(self):
        """Test merging two dicts."""
        src = {"a": 1, "b": 2}
        dest = {"c": 3, "a": "b", 4: "d"}

        merge_data(dest, src)
        self.assertEqual(dest, {"a": 1, "b": 2, "c": 3, 4: "d"})

    def test_merge_objects(self):
        """Test merging two objects."""
        dummy_type = make_type("Dummy", members={"a": 1, "b": 2})
        src = dummy_type()
        src.a = 3
        dest = dummy_type()

        merge_data(dest, src)
        self.assertEqual(dest.a, 3)
        self.assertEqual(dest.b, 2)

    def test_merge_different_objects(self):
        """Test merging two objects of different types."""
        a_type = make_type("A")
        b_type = make_type("B")

        with self.assertRaises(TypeError):
            merge_data([], {1, 2})

        with self.assertRaises(TypeError):
            merge_data(b_type(), a_type())
