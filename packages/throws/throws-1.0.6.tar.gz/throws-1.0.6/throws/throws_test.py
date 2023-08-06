#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from typing import Optional
from .throws import throws, EmptyListException, InvalidRaisedException


class TestThrows(unittest.TestCase):
    """
    Test cases on throws operator provided by this package
    """

    @throws()
    def emptyThrowsList(self):
        """
        1. Testcase: empty list provided to decorator, should fail always with ListEmptyException
        """

        pass


    @throws(ValueError, AssertionError)
    def incompleteThrowsList(self, param: Optional[bool]):
        """
        2. Testcase: incomplete list provided to decorator, should fail when param is None
        """

        if param:
            raise ValueError
        elif param == False:
            raise AssertionError
        else:
            raise IOError


    @throws(ValueError, AssertionError)
    def completeThrowsList(self, param: bool):
        """
        3. Testcase: complete list provided to decorator, should not fail even when param is None
        """

        if param:
            raise ValueError
        else:
            raise AssertionError


    def test_A_emptyThrowsList(self):
        """ test on emptyThrowsList """

        try:
            self.emptyThrowsList()
            ran1 = True
        except EmptyListException:
            ran1 = False

        self.assertFalse(ran1)


    def test_B1_incompleteThrowsList(self):
        """ first test on testIncompleteThrowsList """

        try:
            self.incompleteThrowsList(True)
            ran2 = True
        except ValueError:
            ran2 = False

        self.assertFalse(ran2)


    def test_B2_incompleteThrowsList(self):
        """ second test on testIncompleteThrowsList """

        try:
            self.incompleteThrowsList(False)
            ran3 = True
        except AssertionError:
            ran3 = False

        self.assertFalse(ran3)


    def test_B3_incompleteThrowsList(self):
        """ third test on testIncompleteThrowsList """

        try:
            self.incompleteThrowsList(None)
            ran4 = True
        except InvalidRaisedException:
            ran4 = False

        self.assertFalse(ran4)


    def test_C1_completeThrowsList(self):
        """ first test on testCompleteThrowsList """

        try:
            self.completeThrowsList(True)
            ran5 = True
        except ValueError:
            ran5 = False

        self.assertFalse(ran5)


    def test_C2_completeThrowsList(self):
        """ second test on testCompleteThrowsList """

        try:
            self.completeThrowsList(False)
            ran6 = True
        except AssertionError:
            ran6 = False

        self.assertFalse(ran6)


    def test_C3_completeThrowsList(self):
        """ third test on testCompleteThrowsList """

        try:
            self.completeThrowsList(None)
            ran7 = True
        except AssertionError:
            ran7 = False

        self.assertFalse(ran7)


if __name__ == '__main__':
    unittest.main()
