"""
    @Time    : 06.12.2021 20:42
    @Author  : Subvael
    @File    : Event.py
"""
from airignis.exceptions import *


class Event:

    def __init__(self):
        self._cb_container = list()

    def __iadd__(self, callback_function):
        """
        Add a subscriber to the event

        :param callback_function: Callback function of the subscriber, which input pattern should correspond to the
        invoking statement
        :raise: A CallbackNotCallableError is raised if the passed callback_function is not a callable item
        """
        if not callable(callback_function):
            raise CallbackNotCallableError('The passed argument is not a callable item')

        self._cb_container.append(callback_function)
        return self

    def __isub__(self, callback_function):
        """
        Remove a subscriber from the event

        :param callback_function: Callback function of the subscriber to be removed
        :raise: A CallbackNotCallableError is raised if the passed callback_function is not a callable item
        :raise: A UnsubscribeError is raised if the passed callback function wasn't previously subscribed
        """
        if not callable(callback_function):
            raise CallbackNotCallableError('The passed argument is not a callable item')

        if callback_function not in self._cb_container:
            raise UnsubscribeError

        self._cb_container.remove(callback_function)
        return self

    def invoke(self, *args, **kwargs):
        """Invoke the event and pass the arguments to callback function of all subscribers

        :param args: Positional arguments
        :param kwargs: Keyword arguments
        """
        for cb in self._cb_container:
            cb(*args, **kwargs)

    @property
    def subscriber_callbacks(self):
        """Returns a list containing all subscriber callbacks connected to the event

        :return: Subscriber's callback container
        """
        return self._cb_container
