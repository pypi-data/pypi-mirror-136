"""
    @Time    : 08.12.2021 22:17
    @Author  : Subvael
    @File    : DueTime.py
"""

from airignis.exceptions import *
from datetime import datetime, date, time, timedelta
from dateutil import tz
import math


# @todo: move this implementation into an appropriate package for better share
class TermLogger:
    """This class allows formatted and coloured debugging outputs
    """

    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def print_warning(self, text: str = 'Undefined Waring') -> None:
        print(f'{self.WARNING}WARNING: {text}{self.ENDC}')

    def print_failure(self, text: str = 'Undefined Waring') -> None:
        print(f'{self.FAIL}FAIL: {text}{self.ENDC}')


class DueTime:
    """This class is responsible for the main management of periodic recurring events.

    Represents a due time and some mechanisms to track periodic occurring date and / or time
    rate: Represents the frequency of occurrences for the due time
    rate_unit: Represents the unit in which the rate will be counted
    due_time: DueTime object responsible for the management of the periodic due time occurrences
    due_date: Represents the starting date of the due time object
    instant_zero_ref: Optional: represent how many years in the past the instant zero should be chosen
    """

    def __init__(self, rate: int = 1, rate_unit: str = 'second',
                 due_time: time = time(0, 0, 0, 0), due_date: date = None, instant_zero_ref: int = 50):

        self._rate_unit_types = ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']
        if rate_unit not in self._rate_unit_types:
            raise UndefinedRateUnitError(rate_unit)

        self._rate = 1 if rate == 0 else abs(rate)
        self._rate_unit = rate_unit

        self._timezone = tz.tzutc() if due_time.tzinfo is None else due_time.tzinfo
        self._time = time(int(due_time.hour), int(due_time.minute), int(due_time.second),
                          int(due_time.microsecond), self._timezone)

        """
        Using a date initializer out of the range 1971-3001, the datetime object is restrained and raises os
        exceptions when calling some functions like .astimezone()
        Therefore, we assume the instant zero to always be the first january 50 years behind
        """
        ref_datetime = datetime.now(tz=self._timezone) - timedelta(days=365*instant_zero_ref)
        self._instant_zero = datetime.combine(date(int(ref_datetime.year), 1, 1), time()).astimezone(self._timezone)
        self._next_due = self._instant_zero

        self._date = self._instant_zero.date if due_date is None else due_date
        self._datetime = self._instant_zero if due_date is None else \
                         datetime.combine(due_date, self._time).astimezone(self._timezone)

        self.__counter_skipped_dues = 0

        # This definition is not supported for months and years due to the non constant number of days
        self.__usecond_per_unit = {'second': 1000000, 'minute': 60000000, 'hour': 3600000000, 'day': 86400000000,
                                   'week': 604800000000}
        self.__test_mode = False

    def __str__(self):
        nothing = ''
        plural = 's'
        space = ' '
        plural_rate = self._rate > 1
        valid_datetime = self._datetime != self._instant_zero
        time_info = f'Time: {self.time}, Timezone: {self.timezone}'
        date_time_info = f'{time_info if not valid_datetime else self._datetime.day}'

        return f'DueTime: Every {self.rate if plural_rate else nothing}' \
               f'{space if plural_rate else nothing}{self.rate_unit}{plural if plural_rate else nothing} at ' \
               f'[{date_time_info}]'

    def set_test_mode(self):
        self.__test_mode = True

    @property
    def rate(self):
        """Returns the rate of the current DueTime object

        :return: Execution rate of the DueTime object
        """
        return self._rate

    @property
    def rate_unit(self):
        """Returns the rate unit of the current DueTime object

        :return: Unit used to represent the rate
        """
        return self._rate_unit

    @property
    def date(self):
        """Returns the date of the current DueTime object

        :return: Date targeted by the DueTime
        :raise DateNotConfiguredError: When trying to read non configured date and / or datetime
        """
        if self._date == self._instant_zero.date:
            raise DateNotConfiguredError(f'The date and/or the time attributes where never set')
        return self._date

    @property
    def time(self):
        """Returns the time of the current DueTime object

        :return: Time targeted by the DueTime
        """
        return self._time

    @property
    def date_time(self):
        """Returns the date and time of the current DueTime object

        :return: Datetime targeted by the DueTime
        :raise DateNotConfiguredError: When trying to read non configured date and / or datetime
        """
        if self._datetime == self._instant_zero:
            raise DateNotConfiguredError(f'The date and/or the time attributes where never set')
        return self._datetime

    @property
    def timezone(self):
        """Returns the timezone of the current DueTime object

        :return: Time zone of the DueTime
        """
        return self._timezone

    @property
    def skipped_dues(self):
        """
        :return: Returns the number of skipped due times according to the configured DueTime and the current time
        """
        return self.__counter_skipped_dues

    @property
    def next_due(self) -> datetime:
        """
        Computes the next due time according to the configurations and the current due time.

        The value of the following due is linked to the current date and/or time. The value only changes when the
        previous due date and/or the time has been passed.

        Setting the 29 February as the due day will lead to the 28th being used if the 29th does not exist in the year
        of interest.

        If the day is not defined on a monthly due time, the first of the next month is used as the due date.

        If the date chosen is not defined on a yearly due time, the next day's date is used as the due date.

        If the unit is given in seconds, the due will be executed at the 2nd second after the start.

        :return: The next due time
        """

        if datetime.now(tz=self._timezone) < self._next_due and not self.__test_mode:
            return self._next_due

        if self._next_due == self._instant_zero and self._datetime != self._instant_zero:
            self._next_due = self._datetime
            return self._next_due

        if self._rate_unit == 'second':
            if self._next_due == self._instant_zero:
                useconds_diff = self._time.microsecond - datetime.now(tz=self._timezone).microsecond
                self._next_due = datetime.combine(datetime.now().date(),
                                                  time(hour=datetime.now().hour, minute=datetime.now().minute,
                                                       second=datetime.now().second,
                                                       microsecond=datetime.now().microsecond)
                                                  ).astimezone(self._timezone) + \
                                 timedelta(microseconds=useconds_diff if useconds_diff > 1e6 else useconds_diff + 2e6)

            else:
                self._next_due = self._next_due + timedelta(seconds=self._rate)
                if self._next_due < datetime.now(tz=self._timezone):
                    self._next_due = self._next_due + self.__skipped_dues() * timedelta(seconds=self._rate)

        if self._rate_unit == 'minute':
            if self._next_due == self._instant_zero:
                seconds_diff = self._time.second - datetime.now(tz=self._timezone).second
                self._next_due = datetime.combine(datetime.now().date(),
                                                  time(hour=int(datetime.now().hour), minute=int(datetime.now().minute),
                                                       second=int(datetime.now().second))
                                                  ).astimezone(self._timezone) + \
                                 timedelta(seconds=seconds_diff if seconds_diff > 0 else seconds_diff + 60,
                                           microseconds=self._time.microsecond)
            else:
                self._next_due = self._next_due + timedelta(minutes=self._rate)
                if self._next_due < datetime.now(tz=self._timezone):
                    self._next_due = self._next_due + self.__skipped_dues() * timedelta(minutes=self._rate)

        if self._rate_unit == 'hour':
            if self._next_due == self._instant_zero:
                minutes_diff = self._time.minute - datetime.now(tz=self._timezone).minute
                self._next_due = datetime.combine(datetime.now().date(),
                                                  time(hour=int(datetime.now().hour), minute=int(datetime.now().minute))
                                                  ).astimezone(self._timezone) + \
                                 timedelta(minutes=minutes_diff if minutes_diff > 0 else minutes_diff + 60,
                                           seconds=self._time.second, microseconds=self._time.microsecond)
            else:
                self._next_due = self._next_due + timedelta(hours=self._rate)
                if self._next_due < datetime.now(tz=self._timezone):
                    self._next_due = self._next_due + self.__skipped_dues() * timedelta(hours=self._rate)

        if self._rate_unit == 'day':
            if self._next_due == self._instant_zero:
                hours_diff = self._time.hour - datetime.now(tz=self._timezone).hour
                self._next_due = datetime.combine(datetime.now().date(), time(hour=int(datetime.now().hour))
                                                  ).astimezone(self._timezone) + \
                                 timedelta(hours=hours_diff if hours_diff > 0 else hours_diff + 24,
                                           minutes=self._time.minute, seconds=self._time.second,
                                           microseconds=self._time.microsecond)
            else:
                self._next_due = self._next_due + timedelta(days=self._rate)
                if self._next_due < datetime.now(tz=self._timezone):
                    self._next_due = self._next_due + self.__skipped_dues() * timedelta(days=self._rate)

        if self._rate_unit == 'week':
            if self._next_due == self._instant_zero:
                days_diff = 1 - datetime.now(tz=self._timezone).isoweekday()
                self._next_due = datetime.combine(datetime.now().date(), time()).astimezone(self._timezone) + \
                                 timedelta(days=days_diff if days_diff >= 0 else days_diff + 7, hours=self._time.hour,
                                           minutes=self._time.minute, seconds=self._time.second,
                                           microseconds=self._time.microsecond)
            else:
                self._next_due = self._next_due + timedelta(weeks=self._rate)
                if self._next_due < datetime.now(tz=self._timezone):
                    self._next_due = self._next_due + self.__skipped_dues() * timedelta(weeks=self._rate)

        if self._rate_unit == 'month':
            if self._next_due == self._instant_zero:
                days_diff = 1 - datetime.now(tz=self._timezone).day
                days_offset = self.month_days(int(datetime.now(tz=self._timezone).month))
                self._next_due = datetime.combine(datetime.now().date(), time()).astimezone(self._timezone) + \
                                 timedelta(days=days_diff if days_diff >= 0 else days_diff + days_offset,
                                           hours=self._time.hour, minutes=self._time.minute, seconds=self._time.second,
                                           microseconds=self._time.microsecond)
            else:
                next_month_date = date(self._next_due.year, self._next_due.month, 1) + timedelta(days=31*self._rate)
                self.__set_next_month_due(next_month_date)
                if self._next_due < datetime.now(tz=self._timezone):
                    now = datetime.now(tz=self._timezone)
                    current_year_month = datetime.combine(date(int(now.year), int(now.month), 1), time())
                    next_due_year_month = datetime.combine(date(int(self._next_due.year),
                                                                int(self._next_due.month), 1), time())
                    delta = self.months_diff(current_year_month, next_due_year_month)
                    whole_skipped = math.floor(delta/self._rate) + 1
                    modulo = delta % self._rate
                    tmp_due = datetime.combine(date(now.year, now.month, self._datetime.day), self._time
                                               ).astimezone(self._timezone)

                    """
                    If the modulo == 0 then the current month is a due month. we only need to find out if the exact
                    due day, and time were already missed or not to design the appropriate solution
                    """
                    if modulo == 0 and tmp_due >= datetime.now(tz=self._timezone):
                        self._next_due = tmp_due
                        self.__counter_skipped_dues = whole_skipped - 1

                    if modulo == 0 and tmp_due < datetime.now(tz=self._timezone):
                        self._next_due = self.add_months(tmp_due, self._rate)
                        self.__counter_skipped_dues = whole_skipped

                    """
                    If the modulo is different than zero, the whole_skipped variable representing the whole term
                    of the delta division added with 1, then counts for the amount of skipped due dates. the next_due
                    is thus obtained by using the number of skipped due dates
                    """
                    if modulo != 0:
                        self._next_due = self.add_months(self._next_due, whole_skipped * self._rate)
                        self.__counter_skipped_dues = whole_skipped

                    self._notify_if_skipped_dues()

        if self._rate_unit == 'year':
            if self._next_due == self._instant_zero:
                self._datetime = datetime.combine(datetime.now() + timedelta(days=1),
                                                  self._time).astimezone(self._timezone)
                self._date = self._datetime.date()
                self._next_due = self._datetime
            else:
                year = int(self._next_due.year) + self._rate
                month = int(self._datetime.month)
                self._next_due = datetime.combine(date(year, month,
                                                       int(self.safe_date(year, month, int(self._datetime.day)).day)),
                                                  self._time).astimezone(self._timezone)
                if self._next_due < datetime.now(tz=self._timezone):
                    current_year = datetime.now(tz=self._timezone).year
                    delta = int(current_year - self._next_due.year)
                    whole_skipped = math.floor(delta/self._rate) + 1
                    modulo = delta % self._rate
                    tmp_due = datetime.combine(date(current_year, self._datetime.month, self._datetime.day), self._time
                                               ).astimezone(self._timezone)

                    """ 
                    If the modulo == 0 then the current year is a due year. we only need to find out if the exact
                    due month, day, and time were skipped or not to design the appropriate solution
                    """
                    if modulo == 0 and tmp_due >= datetime.now(tz=self._timezone):
                        self._next_due = tmp_due
                        self.__counter_skipped_dues = whole_skipped - 1

                    if modulo == 0 and tmp_due < datetime.now(tz=self._timezone):
                        self._next_due = datetime.combine(date(tmp_due.year + self._rate, self._datetime.month,
                                                               self._datetime.day), self._time
                                                          ).astimezone(self._timezone)
                        self.__counter_skipped_dues = whole_skipped

                    """
                    If the modulo is different than zero, the whole_skipped variable representing the whole term
                    of the delta division added with 1 then counts for the amount of skipped due dates. The next_due
                    is thus obtained by using the number of skipped due dates 
                    """
                    if modulo != 0:
                        self._next_due = datetime.combine(date(self._next_due.year + self._rate * whole_skipped,
                                                               self._datetime.month, self._datetime.day), self._time
                                                          ).astimezone(self._timezone)
                        self.__counter_skipped_dues = whole_skipped

                    self._notify_if_skipped_dues()

        return self._next_due

    def _notify_if_skipped_dues(self) -> None:
        """
        Prints a warning notification if due times has been skipped
        """
        # @todo: Add a warning in the log system to notify, that a due time has been skipped
        # @todo: move the terminal_logger to an appropriate location of better share
        if self.__counter_skipped_dues > 0 and not self.__test_mode:
            skip_plural = 's' if self.__counter_skipped_dues > 1 else ''
            terminal_logger = TermLogger()
            terminal_logger.print_warning(f'{self.__counter_skipped_dues} Due time{skip_plural} had been skipped !!')

    def __skipped_dues(self) -> int:
        """
        Counts and returns the skipped dues. This function should only be called after detecting a skipped due. This
        requirement also prevents divisions by zero (Thus i set it private) (Not supported for months and years)
        :return: Number of skipped dues
        """
        delta = datetime.now(tz=self._timezone) - self._next_due
        due_interval = self._rate * self.__usecond_per_unit[self._rate_unit]
        self.__counter_skipped_dues = math.floor(int(1e6 * delta.total_seconds()) / due_interval) + 1
        self._notify_if_skipped_dues()
        return self.__counter_skipped_dues

    def __set_next_month_due(self, next_month_date: date) -> None:
        """
        Internal function to set the monthly's next due
        :param next_month_date: The monthly upgraded next due time
        """
        year = int(next_month_date.year)
        month = int(next_month_date.month)
        eval_date = self.safe_date(year, month, int(self._datetime.day))
        self._next_due = datetime.combine(date(year, month, int(eval_date.day)), self._time).astimezone(self._timezone)

    @staticmethod
    def month_days(month: int, year: int = None) -> int:
        """
        Computes the number of days in the passed month. the months are ranged from 1 to 12 (January to December)
        :param month: Month of interest
        :param year: Year of interest. If not given, the current year is used
        :return: The number of days is returned as an integer value between 1 to 31
        """
        next_month_date = date((datetime.now().year if year is None else year), month, 1) + timedelta(days=31)
        return int((next_month_date -
                    date((datetime.now().year if year is None else year), month, next_month_date.day)).days)

    @staticmethod
    def date_exist(day: int, month: int = None, year: int = None) -> bool:
        """
        This function returns True if the input dat is valid and False if not
        :param day: Day to be evaluated
        :param month: Month to be evaluated. Current month is used if None
        :param year: Year to be evaluated. Current year is used if None
        :return: True if date exist, false if not
        """
        _year = int(datetime.now().year) if year is None else year
        _month = int(datetime.now().month) if month is None else month
        try:
            date(_year, _month, day)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def safe_date(year: int, month: int, day: int) -> date:
        """
        This function implements a day correction on the passed datetime. A correction might be required due to
        monthly/yearly dependent non existing days (Ex: February 29)
        :param year: Input year to be evaluated
        :param month: Input month to be evaluated
        :param day: Input day to be evaluated
        :return: An adapted datetime is computed and returned
        """
        while not DueTime.date_exist(day, month, year):
            day -= 1
        return date(year, month, day)

    @staticmethod
    def add_months(source: datetime, months: int) -> datetime:
        """
        Adds the passed amount of months to the source_datetime
        :param source: Datetime to which the months are added
        :param months: Number of months to be added to the source datetime
        :return: Datetime with the added amount of months
        """
        year, month = divmod(source.month + months, 12)
        if month == 0:
            month = 12
            year = year - 1

        safe_date = DueTime.safe_date(source.year + year, month, source.day)
        return datetime(safe_date.year, safe_date.month, safe_date.day, source.time().hour, source.time().minute,
                        source.time().second, source.time().microsecond, source.tzinfo)

    @staticmethod
    def months_diff(a: datetime, b: datetime) -> int:
        """
        This functions computes the month difference between the two passed datetimes the order does not matters
        :param a: first datetime
        :param b: second datetime
        :return: An integer is returned representing the number of months separating both datetimes
        """
        dec_a = int(a.year) + (int(a.month) / 12.12)
        dec_b = int(b.year) + (int(b.month) / 12.12)
        delta = dec_a - dec_b if dec_a > dec_b else dec_b - dec_a
        delta_round = math.floor(delta)
        month_ratio_in_year = DueTime.round_down((1 / 12.12), 11)
        months = 12 * delta_round + math.floor((delta - delta_round) / month_ratio_in_year)
        return months

    @staticmethod
    def round_down(value: float, decimals: int) -> float:
        """
        This function rounds down to the passed number of decimals
        :param value: Value to be round down
        :param decimals: Number of decimals
        :return: input value rounded down
        :raise ValueError: Raised if input types are not correct
        """
        if not isinstance(value, (int, float)):
            raise ValueError

        if not isinstance(decimals, int):
            raise ValueError

        if isinstance(value, int):
            return value

        factor = 1 / (10 ** decimals)
        return (value // factor) * factor
