#!/usr/bin/python3
# @Time    : 2022-06-23
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from autils.date import DateTool

class TestDateTool(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.year = 2020
        cls.month = 2

    def test_get_month_range(self):
        first_day, last_day = DateTool.get_first_and_last_day(self.year,self.month)
        print(first_day,last_day)
    

if __name__ == "__main__":
    unittest.main()