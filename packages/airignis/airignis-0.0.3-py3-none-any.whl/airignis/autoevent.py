"""
    @Time    : 08.12.2021 21:36
    @Author  : Subvael
    @File    : AutoEvent.py
"""

import threading
from datetime import datetime
from airignis import DueTime
from enum import Enum


class AutoEventState(Enum):
    """
    Represents the current state of the auto event
    """
    UNDEFINED = 0
    RUNNING = 1
    STOPPED = 2


class AutoEvent(threading.Thread):
    # @todo: Implement missing functionalities (safe abort; ... )

    def __init__(self, job, due_time: DueTime = None, stop: datetime = None, *args, **kwargs):
        super().__init__()

        self._due_time = due_time
        self._stop_datetime = stop
        self.__stop_event = threading.Event()
        self.args = args
        self.kwargs = kwargs
        self._job = job
        self._state = AutoEventState.UNDEFINED

    def __sleep_time(self):
        """
        Computes the amount of seconds up to which the auto even thread will sleep before the next due time
        :return: The sleep time is returned
        """

        if datetime.now(self._due_time.timezone) > self._due_time.next_due:
            return 0

        sleep_time_tmp = (self._due_time.next_due - datetime.now(self._due_time.timezone)).total_seconds()

        return sleep_time_tmp if sleep_time_tmp > 0 else 0

    @property
    def is_stop_time(self):
        """
        Is stop time property
        :return: True is returned when comes the time to stop
        """
        return datetime.now(self._due_time.timezone) > self._stop_datetime

    @property
    def state(self):
        return self._state

    def stop(self):
        """
        This command interrupts the auto event execution
        """
        self.__stop_event.set()

    def run(self):
        """
        Override of the Thread's run() function
        """
        self._state = AutoEventState.RUNNING
        while not self.__stop_event.wait(self.__sleep_time()):
            if self.is_stop_time:
                return
            self._job(*self.args, **self.kwargs)

        self._state = AutoEventState.STOPPED
