"""
    @Time    : 08.12.2021 22:42
    @Author  : Subvael
    @File    : DueTime_test.py
"""

import unittest
from airignis import DueTime
from datetime import datetime, time, date, timedelta
from airignis.exceptions import *
from dateutil import tz
import pytz


class DueTimeTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_due_time_1 = DueTime(-2, 'day')
        self.test_due_time_2 = DueTime(0, 'day')
        self.test_due_time_3: DueTime = None
        self.test_due_time_4 = DueTime(3, 'week', time(0, 0, 0, 0), date(2000, 1, 1))
        self.test_due_time_5 = DueTime(1, 'month', time(15, 10, 30, 800, tzinfo=tz.gettz('Europe/Berlin')))
        self.test_due_time_6 = DueTime(2, 'year', time(15, 10, 30, 800, tzinfo=tz.gettz('Europe/Berlin')),
                                       date(2018, 12, 18))

    def test_read_sufficiently_configured_due_time(self):
        self.assertEqual(self.test_due_time_4.date_time, datetime.combine(date(2000, 1, 1),
                                                                          time(0, 0, 0, 0, tz.tzutc())))

    def create_due_time_with_undefined_unit(self):
        self.test_due_time_3 = DueTime(1, 'undefined_unit')

    def test_raise_if_undefined_unit(self):
        self.assertRaises(UndefinedRateUnitError, self.create_due_time_with_undefined_unit)

    def print_date_time_property(self):
        print(self.test_due_time_2.date_time)

    def test_date_time_not_configured(self):
        self.assertRaises(DateNotConfiguredError, self.print_date_time_property)

    def test_negative_rate_input_handling(self):
        self.assertEqual(self.test_due_time_1.rate, 2)

    def test_null_rate_input_handling(self):
        self.assertEqual(self.test_due_time_2.rate, 1)

    def test_print_due_time_object_properly(self):
        self.assertEqual(str(self.test_due_time_1), 'DueTime: Every 2 days at [Time: 00:00:00+00:00, Timezone: tzutc()]')
        pass

    def test_month_days(self):
        self.assertEqual(DueTime.month_days(12), 31)
        self.assertEqual(DueTime.month_days(4, 2022), 30)
        self.assertEqual(DueTime.month_days(6, 2022), 30)
        self.assertEqual(DueTime.month_days(1, 1050), 31)
        self.assertEqual(DueTime.month_days(9, 1050), 30)
        self.assertEqual(DueTime.month_days(2, 1050), 28)
        self.assertEqual(DueTime.month_days(2, 1061), 28)
        self.assertEqual(DueTime.month_days(5, 1061), 31)
        self.assertEqual(DueTime.month_days(8, 1185), 31)
        self.assertEqual(DueTime.month_days(11, 1185), 30)

    def test_months_diff(self):
        self.assertEqual(DueTime.months_diff(datetime(2000, 1, 1), datetime(2010, 1, 1)), 120)
        self.assertEqual(DueTime.months_diff(datetime(2000, 1, 1), datetime(2110, 6, 2)), 1325)
        self.assertEqual(DueTime.months_diff(datetime(2026, 2, 1), datetime(2026, 1, 12)), 1)
        self.assertEqual(DueTime.months_diff(datetime(2000, 1, 1), datetime(2010, 3, 27)), 122)

    def test_months_diff_order_insensitivity(self):
        self.assertEqual(DueTime.months_diff(datetime(2000, 1, 1), datetime(2010, 5, 1)), 124)
        self.assertEqual(DueTime.months_diff(datetime(2010, 5, 1), datetime(2000, 1, 1)), 124)

    def test_round_down(self):
        self.assertEqual(DueTime.round_down(26.669, 2), 26.66)
        self.assertEqual(DueTime.round_down(60, 2), 60)
        self.assertEqual(DueTime.round_down(999999999.66552336699859, 13), 999999999.6655233669985)

    def call_round_down_with_string_value(self):
        DueTime.round_down('cat', 2)

    def test_round_down_invalid_value(self):
        self.assertRaises(ValueError, self.call_round_down_with_string_value)

    def call_round_down_with_float_decimals(self):
        DueTime.round_down(24.5563, 2.3)

    def test_round_down_invalid_decimals(self):
        self.assertRaises(ValueError, self.call_round_down_with_float_decimals)

    def test_add_months(self):
        self.assertEqual(DueTime.add_months(datetime(2021, 12, 18), 3), datetime(2022, 3, 18))

    def test_add_months_time_consistency(self):
        self.assertEqual(DueTime.add_months(datetime(2021, 12, 18, 17, 30, 10, 600), 3),
                         datetime(2022, 3, 18, 17, 30, 10, 600))

    def test_add_months_timezone_consistency(self):
        self.assertEqual(DueTime.add_months(datetime(2021, 12, 18, 0, 0, 0, 0, tz.gettz("US/Mountain")), 3),
                         datetime(2022, 3, 18, 0, 0, 0, 0, tz.gettz("US/Mountain")))

    def test_add_months_days_robustness(self):
        self.assertEqual(DueTime.add_months(datetime(2021, 12, 31, 0, 0, 0, 0, tz.gettz("US/Mountain")), 2),
                         datetime(2022, 2, 28, 0, 0, 0, 0, tz.gettz("US/Mountain")))

    def test_add_months_negative_value(self):
        self.assertEqual(DueTime.add_months(datetime(2021, 12, 31, 0, 0, 0, 0, tz.gettz("GMT")), -2),
                         datetime(2021, 10, 31, 0, 0, 0, 0, tz.gettz("GMT")))

    def test_add_months_negative_value_at_jan(self):
        self.assertEqual(DueTime.add_months(datetime(2021, 1, 1, 0, 0, 0, 0, tz.gettz("GMT")), -2),
                         datetime(2020, 11, 1, 0, 0, 0, 0, tz.gettz("GMT")))

    def test_next_due_year_not_skipped(self):
        now = datetime.now(tz=tz.gettz('Navajo'))
        rate = 2
        test_due = DueTime(rate, 'year', time(15, 10, 30, 800, tzinfo=tz.gettz('Navajo')),
                           date(now.year - int(rate/2), 12, 18))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(now.year - int(rate/2), 12, 18,
                                                     15, 10, 30, 800, tzinfo=tz.gettz('Navajo')))
        self.assertEqual(test_due.next_due, datetime(now.year + int(rate/2), 12, 18,
                                                     15, 10, 30, 800, tzinfo=tz.gettz('Navajo')))
        self.assertEqual(test_due.skipped_dues, 0)

    def test_next_due_year_skipped_not_due_year(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        rate = 2
        test_due = DueTime(rate, 'year', time(15, 10, 30, 800, tzinfo=tz.gettz('Europe/Berlin')),
                           date(now.year - rate - 1, 12, 18))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(now.year - rate - 1, 12, 18,
                                                     15, 10, 30, 800, tzinfo=tz.gettz('Europe/Berlin')))
        self.assertEqual(test_due.next_due, datetime(now.year + 1, 12, 18,
                                                     15, 10, 30, 800, tzinfo=tz.gettz('Europe/Berlin')))
        self.assertEqual(test_due.skipped_dues, 1)

    def test_next_due_year_skipped_due__due_before_date(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        test_date = now - timedelta(hours=1)
        rate = 3
        test_due = DueTime(rate, 'year', time(test_date.hour, test_date.minute, test_date.second,
                                              test_date.microsecond, tzinfo=tz.gettz('Europe/Berlin')),
                           date(test_date.year - rate * 2, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(test_date.year - rate * 2, test_date.month, test_date.day,
                                                     test_date.hour, test_date.minute, test_date.second,
                                                     test_date.microsecond, tzinfo=tz.gettz('Europe/Berlin')))

        self.assertEqual(test_due.next_due, datetime(test_date.year + rate, test_date.month, test_date.day,
                                                     test_date.hour, test_date.minute, test_date.second,
                                                     test_date.microsecond, tzinfo=tz.gettz('Europe/Berlin')))

        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_year_skipped_due__due_after_date(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        test_date = now + timedelta(hours=1)
        rate = 3
        test_due = DueTime(rate, 'year', time(test_date.hour, test_date.minute, test_date.second,
                                              test_date.microsecond, tzinfo=tz.gettz('Europe/Berlin')),
                           date(test_date.year - rate * 2, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(test_date.year - rate * 2, test_date.month, test_date.day,
                                                     test_date.hour, test_date.minute, test_date.second,
                                                     test_date.microsecond, tzinfo=tz.gettz('Europe/Berlin')))
        self.assertEqual(test_due.next_due, test_date)

        self.assertEqual(test_due.skipped_dues, 1)

    def test_next_due_month_not_skipped(self):
        now = datetime.now(tz=tz.gettz('Japan'))
        test_date = now + timedelta(hours=1)
        rate = 2
        test_date = DueTime.add_months(test_date, -int(rate / 2))
        test_due = DueTime(rate, 'month', time(15, 10, 30, 800, tzinfo=tz.gettz('Japan')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(test_date.year, test_date.month, test_date.day,
                                                     15, 10, 30, 800, tzinfo=tz.gettz('Japan')))
        self.assertEqual(test_due.next_due, DueTime.add_months(datetime(test_date.year, test_date.month, test_date.day,
                                                                        15, 10, 30, 800, tzinfo=tz.gettz('Japan')), rate))
        self.assertEqual(test_due.skipped_dues, 0)

    def test_next_due_month_skipped__not_due_month(self):
        now = datetime.now(tz=tz.tzutc())
        test_date = now + timedelta(hours=1)
        rate = 3
        test_date = DueTime.add_months(test_date, -rate*2 - 1)
        test_due = DueTime(rate, 'month', time(15, 10, 30, 800),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(test_date.year, test_date.month, test_date.day,
                                                     15, 10, 30, 800, tzinfo=tz.tzutc()))
        self.assertEqual(test_due.next_due, DueTime.add_months(datetime(test_date.year, test_date.month, test_date.day,
                                                                        15, 10, 30, 800, tzinfo=tz.tzutc()), rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_month_skipped__due_month_before_date(self):
        now = datetime.now(tz=tz.tzutc())
        test_date = now - timedelta(hours=1)
        rate = 3
        test_date = DueTime.add_months(test_date, -rate*2)
        test_due = DueTime(rate, 'month',
                           time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, DueTime.add_months(test_date, rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_month_skipped__due_month_after_date(self):
        now = datetime.now(tz=tz.tzutc())
        test_date = now + timedelta(hours=1)
        rate = 3
        test_date = DueTime.add_months(test_date, -rate*2)
        test_due = DueTime(rate, 'month',
                           time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, DueTime.add_months(test_date, rate*2))
        self.assertEqual(test_due.skipped_dues, 1)

    def test_next_due_day_not_skipped(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        rate = 2
        test_date = now - timedelta(days=int(rate / 2))
        test_due = DueTime(rate, 'day', time(15, 10, 30, 800, tzinfo=tz.gettz('Europe/Berlin')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(test_date.year, test_date.month, test_date.day,
                                                     15, 10, 30, 800, tzinfo=tz.gettz('Europe/Berlin')))
        self.assertEqual(test_due.next_due, datetime(test_date.year, test_date.month, test_date.day, 15, 10,
                                                     30, 800, tzinfo=tz.gettz('Europe/Berlin')) + timedelta(days=rate))
        self.assertEqual(test_due.skipped_dues, 0)

    def test_next_due_day_skipped__not_due_day(self):
        now = datetime.now(tz=tz.gettz('Europe/Zurich'))
        rate = 3
        test_date = now - timedelta(days=int(rate*2 + 1))
        test_due = DueTime(rate, 'day', time(15, 10, 30, 800, tzinfo=tz.gettz('Europe/Zurich')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, datetime(test_date.year, test_date.month, test_date.day,
                                                     15, 10, 30, 800, tzinfo=tz.gettz('Europe/Zurich')))
        self.assertEqual(test_due.next_due, datetime(test_date.year, test_date.month, test_date.day, 15, 10, 30, 800,
                                                     tzinfo=tz.gettz('Europe/Zurich')) + timedelta(days=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_day_skipped__due_day_before_date(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        rate = 3
        test_date = now - timedelta(days=int(rate*2), hours=2)
        test_due = DueTime(rate, 'day', time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond,
                                             tzinfo=tz.gettz('Europe/Berlin')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(days=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_day_skipped__due_day_after_date(self):
        now = datetime.now(tz=tz.gettz('Asia/Hong_Kong'))
        rate = 3
        test_date = now - timedelta(days=int(rate*2), hours=-2)
        test_due = DueTime(rate, 'day', time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond,
                                             tzinfo=tz.gettz('Asia/Hong_Kong')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(days=rate*2))
        self.assertEqual(test_due.skipped_dues, 1)

    def test_next_due_hour_not_skipped(self):
        now = datetime.now(tz=tz.gettz('Mexico/General'))
        rate = 2
        test_date = now - timedelta(hours=int(rate / 2))
        test_due = DueTime(rate, 'hour', time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond,
                                             tzinfo=tz.gettz('Mexico/General')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(hours=rate))
        self.assertEqual(test_due.skipped_dues, 0)

    def test_next_due_hour_skipped__not_due_hour(self):
        now = datetime.now(tz=tz.gettz('Asia/Kolkata'))
        rate = 2
        test_date = now - timedelta(hours=int(rate*2 + 1))
        test_due = DueTime(rate, 'hour', time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond,
                                              tzinfo=tz.gettz('Asia/Kolkata')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(hours=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_hour_skipped__due_hour_before_date(self):
        now = datetime.now(tz=tz.gettz('Asia/Singapore'))
        rate = 2
        test_date = now - timedelta(hours=int(rate*2))
        test_due = DueTime(rate, 'hour', time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond,
                                              tzinfo=tz.gettz('Asia/Singapore')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(hours=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_hour_skipped__due_hour_after_date(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        rate = 2
        test_date = now - timedelta(hours=int(rate*2))
        test_due = DueTime(rate, 'hour', time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond,
                                              tzinfo=tz.gettz('Europe/Berlin')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(hours=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_minute_not_skipped(self):
        now = datetime.now(tz=tz.gettz('Africa/Johannesburg'))
        rate = 2
        test_date = now - timedelta(minutes=int(rate / 2))
        test_due = DueTime(rate, 'minute', time(test_date.hour, test_date.minute, test_date.second, test_date.microsecond,
                                             tzinfo=tz.gettz('Africa/Johannesburg')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(minutes=rate))
        self.assertEqual(test_due.skipped_dues, 0)

    def test_next_due_minute_skipped__not_due_minute(self):
        now = datetime.now(tz=tz.gettz('Europe/Amsterdam'))
        rate = 2
        test_date = now - timedelta(minutes=int(rate*2 + 1))
        test_due = DueTime(rate, 'minute', time(test_date.hour, test_date.minute, test_date.second,
                                                test_date.microsecond, tzinfo=tz.gettz('Europe/Amsterdam')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(minutes=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_minute_skipped__due_minute_before_date(self):
        now = datetime.now(tz=tz.gettz('Europe/Paris'))
        rate = 2
        test_date = now - timedelta(minutes=int(rate*2))
        test_due = DueTime(rate, 'minute', time(test_date.hour, test_date.minute, test_date.second,
                                                test_date.microsecond, tzinfo=tz.gettz('Europe/Paris')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(minutes=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_minute_skipped__due_minute_after_date(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        rate = 2
        test_date = now - timedelta(minutes=int(rate*2))
        test_due = DueTime(rate, 'minute', time(test_date.hour, test_date.minute, test_date.second,
                                                test_date.microsecond, tzinfo=tz.gettz('Europe/Berlin')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(minutes=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_second_not_skipped(self):
        now = datetime.now(tz=tz.gettz('US/Mountain'))
        rate = 2
        test_date = now - timedelta(seconds=int(rate / 2))
        test_due = DueTime(rate, 'second', time(test_date.hour, test_date.minute, test_date.second,
                                                test_date.microsecond, tzinfo=tz.gettz('US/Mountain')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(seconds=rate))
        self.assertEqual(test_due.skipped_dues, 0)

    def test_next_due_second_skipped__not_due_second(self):
        now = datetime.now(tz=tz.gettz('Africa/Douala'))
        rate = 2
        test_date = now - timedelta(seconds=int(rate*2 + 1))
        test_due = DueTime(rate, 'second', time(test_date.hour, test_date.minute, test_date.second,
                                                test_date.microsecond, tzinfo=tz.gettz('Africa/Douala')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(seconds=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_second_skipped__due_second_before_date(self):
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        rate = 2
        test_date = now - timedelta(seconds=int(rate*2))
        test_due = DueTime(rate, 'second', time(test_date.hour, test_date.minute, test_date.second,
                                                test_date.microsecond, tzinfo=tz.gettz('Europe/Berlin')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(seconds=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)

    def test_next_due_second_skipped__due_second_after_date(self):
        now = datetime.now(tz=tz.gettz('US/Pacific'))
        rate = 2
        test_date = now - timedelta(seconds=int(rate*2))
        test_due = DueTime(rate, 'second', time(test_date.hour, test_date.minute, test_date.second,
                                                test_date.microsecond, tzinfo=tz.gettz('US/Pacific')),
                           date(test_date.year, test_date.month, test_date.day))
        # Allowing the object to compute more due times than just the next one
        test_due.set_test_mode()
        self.assertEqual(test_due.next_due, test_date)
        self.assertEqual(test_due.next_due, test_date + timedelta(seconds=rate*3))
        self.assertEqual(test_due.skipped_dues, 2)


if __name__ == '__main__':
    unittest.main()
