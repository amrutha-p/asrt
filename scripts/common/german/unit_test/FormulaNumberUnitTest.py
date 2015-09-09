#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of asrt.

# asrt is free software: you can redistribute it and/or modify
# it under the terms of the BSD 3-Clause License as published by
# the Open Source Initiative.

# asrt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# BSD 3-Clause License for more details.

# You should have received a copy of the BSD 3-Clause License
# along with asrt. If not, see <http://opensource.org/licenses/>.

__author__ = "Alexandre Nanchen"
__version__ = "Revision: 1.0"
__date__ = "Date: 2015/09"
__copyright__ = "Copyright (c) 2015 Idiap Research Institute"
__license__ = "BSD 3-Clause"

import unittest
from german.FormulaNumber import NumberFormula

class FormulaNumberUnitTest(unittest.TestCase):

    testDict = { "cardinal": [(u"10",u"zehn"),(u"25",u"fünf und zwanzig")],
                 "ordinal" : [(u"1.",u"erste"),(u"2.",u"zweite"),
                              (u"V.",u"fünfte"), (u"X.",u"zehnte")],
                 "decimal" : [(u"2,5",u"zwei komma fünf"), (u"2.5,3",u"zwei punkt fünf komma drei")],
                 "roman"   : [(u"V",u"fünf"), (u"X",u"zehn"),(u"II",u"zwei")],
                 "all"     : [(u"1ab",u"1ab"),(u"ab",u"ab"),
                              (u"die 25 März 2015 2.5 X.",u"die fünf und zwanzig März zwei tausend fünfzehn zwei punkt fünf zehnte"),
                              (u"21. dezember 2011",u"ein und zwanzigste dezember zwei tausend elf")]
    }

    #################
    # Implementation
    #
    def evaluateListValues(self, testList, callback):
       for t, gt in testList:
            r = callback(t).encode('utf-8')
            self.assertEquals(gt.encode('utf-8'), r, r)

    #################
    # Unit tests
    #
    def test_isCardinal(self):
        testList = [(u"2",True),(u"123",True), (u"123.",False)]

        for t, gt in testList:
            self.assertEquals(NumberFormula._isCardinalNumber(t), gt, t.encode('utf-8'))

    def test_isOrdinal(self):
        testList = [(u"1.",True), (u"3.",True), (u"8.",True), (u"2.",True), (u"10.",True), 
                    (u"I.",True),(u"XII.",True)]

        for t, gt in testList:
            self.assertEquals(NumberFormula._isOrdinalNumber(t), gt, t.encode('utf-8'))

    def test_isDecimal(self):
        testList = [(u"2.5",True), (u"2,5",True),(u"2,5,3",True), (u"2-5",False)]

        for t, gt in testList:
            self.assertEquals(NumberFormula._isDecimalNumber(t), gt, t.encode('utf-8'))

    def test_isRoman(self):
        testList = [(u"V",True), (u"XII",True)]

        for t, gt in testList:
            self.assertEquals(NumberFormula._isRomanNumber(t), gt, t.encode('utf-8'))

    def test_hasNumber(self):
        testList = [(u"12",True), (u"1ab",True),(u"ab22",True), (u"Xab",True),
                    (u"xab",False), (u"a1ab",True)]

        for t, gt in testList:
            self.assertEquals(NumberFormula._hasNumber(t), gt, t.encode('utf-8'))

    def test_normalizeNumber(self):
        testList = [(u"50'000",u"50000"),(u"550'000'000",u"550000000")]
        self.evaluateListValues(testList, NumberFormula._normalizeNumber)

    def test_cardinal2word(self):
        testList = self.testDict["cardinal"]
        self.evaluateListValues(testList, NumberFormula._cardinal2word)

    def test_ordinal2word(self):
        testList = self.testDict["ordinal"]
        self.evaluateListValues(testList, NumberFormula._ordinal2word)

    def test_decimal2word(self):
        testList = self.testDict["decimal"]
        self.evaluateListValues(testList, NumberFormula._decimal2word)

    def test_roman2word(self):
        testList = self.testDict["roman"]
        self.evaluateListValues(testList, NumberFormula._roman2word)

    def test_apply(self):
        f = NumberFormula()

        for k in self.testDict.keys():
            #print "Testing %s " % k
            testList = self.testDict[k]
            self.evaluateListValues(testList, f.apply)
