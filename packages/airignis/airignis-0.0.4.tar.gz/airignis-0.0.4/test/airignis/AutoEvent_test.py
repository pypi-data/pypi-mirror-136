"""
    @Time    : 12.12.2021 01:00
    @Author  : Subvael
    @File    : AutoEvent_test.py
"""

import unittest
from airignis import DueTime, AutoEvent, AutoEventState
from datetime import datetime, timedelta, time
import time as t
from dateutil import tz

auto_events_counter = 0
execution_time = datetime.now(tz=tz.tzutc())
old_time = execution_time

auto_events_counter_min = 0
execution_time_min = datetime.now(tz=tz.tzutc())
old_time_min = execution_time


# @todo: Add unit tests
class AutoEventTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_hello_and_evaluate_elapsed_time(self, name: str, secs_to_be_elapsed: float, float_precision: int):

        execution_time_tmp = datetime.now(tz=tz.tzutc())
        global execution_time
        global old_time

        old_time = execution_time
        execution_time = execution_time_tmp
        global auto_events_counter

        elapsed_time = execution_time - old_time
        print(f"Hello {name}")

        # the first call might occur before the defined rate,
        if auto_events_counter >= 1:
            self.assertAlmostEqual(elapsed_time.total_seconds(), secs_to_be_elapsed, float_precision)

        auto_events_counter += 1

    def print_hello_and_evaluate_elapsed_min(self, name: str, secs_to_be_elapsed: float, float_precision: int):

        execution_time_tmp = datetime.now(tz=tz.tzutc())
        global execution_time_min
        global old_time_min

        old_time_min = execution_time_min
        execution_time_min = execution_time_tmp
        global auto_events_counter_min

        elapsed_time = execution_time - old_time
        print(f"Hello {name}")

        # the first call might occur before the defined rate,
        if auto_events_counter_min >= 1:
            self.assertAlmostEqual(elapsed_time.total_seconds(), secs_to_be_elapsed, float_precision)

        auto_events_counter_min += 1

    def test_auto_event_seconds_execution(self):
        global auto_events_counter

        rate = 2
        seconds_nr = 20
        execution_nr = int(seconds_nr/rate)

        # Creating a test due time which is reproduced every 2 seconds
        test_due_time = DueTime(rate)

        # Defining the stop date time of the auto event. Should stop after 20 seconds thus executes 11 times
        stop_datetime = datetime.now(test_due_time.timezone) + timedelta(seconds=seconds_nr)

        # Creating the auto event handler with a callback function that will be executed according to the due time
        # and stop at the defined stop time
        test_event = AutoEvent(self.print_hello_and_evaluate_elapsed_time, test_due_time, stop_datetime,
                               'world', rate*1.0, 1)

        #  starting the auto event handler
        test_event.start()

        while True:
            self.assertLessEqual(auto_events_counter, execution_nr+1)
            if auto_events_counter >= execution_nr:
                break

    def test_auto_event_minutes_and_stop_function(self):
        global auto_events_counter_min

        rate = 1
        minutes_nr = 4
        execution_nr = int(minutes_nr/rate)

        # Creating a test due time which is reproduced every 2 seconds
        now = datetime.now(tz=tz.gettz('Europe/Berlin'))
        test_due_time = DueTime(1, 'minute', time(hour=now.hour))

        # Defining the stop date time of the auto event. Should stop after 20 seconds thus executes 11 times
        stop_datetime = datetime.now(test_due_time.timezone) + timedelta(minutes=minutes_nr)

        # Creating the auto event handler with a callback function that will be executed according to the due time
        # and stop at the defined stop time
        test_event = AutoEvent(self.print_hello_and_evaluate_elapsed_min, test_due_time, stop_datetime,
                               'world', 60*rate*1.0, 1)

        #  starting the auto event handler
        test_event.start()

        while True:
            self.assertLessEqual(auto_events_counter_min, execution_nr+1)
            if auto_events_counter_min >= 1:
                test_event.stop()
                break

        t.sleep(2)
        self.assertEqual(test_event.state, AutoEventState.STOPPED)


if __name__ == '__main__':
    unittest.main()
