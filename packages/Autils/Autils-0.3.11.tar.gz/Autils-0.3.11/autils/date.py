#!/usr/bin/python3
# @Time    : 2022-06-23
# @Author  : Kevin Kong (kfx2007@163.com)

import datetime
import calendar


class DateTool(object):

    @classmethod
    def get_current_month_range(self):
        """获取当前月份范围"""
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        return self.get_first_and_last_day(year, month)

    @classmethod
    def get_first_and_last_day(self, year, month):
        """
        获取指定年月的第一天和最后一天

        :params
        :year: 年份
        :month :月份

        :Return 指定月份的第一天和最后一天.        
        """

        weekday, month_count_day = calendar.monthrange(year, month)
        first_day = datetime.date(year, month, day=1)
        last_day = datetime.date(year, month, day=month_count_day)
        return first_day, last_day
