"""
    @Time    : 06.12.2021 21:09
    @Author  : Subvael
    @File    : Event_test.py
"""

from airignis import Event
from airignis.exceptions import *
import unittest


global_test_string = 0


def do_something(data):
    global global_test_string
    global_test_string = f'doing something with {data} ...'


class TestConsumer:

    def __init__(self):
        self.consumer_event = Event()

    def invoke_event(self, data):
        self.consumer_event.invoke(data)


class EventTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.consumer = TestConsumer()

    def add_non_callable_callback(self):
        self.consumer.consumer_event += 'cat'

    def test_raise_if_subscribing_non_callable_callback(self):
        self.assertRaises(CallbackNotCallableError, self.add_non_callable_callback)

    def test_add_event_callback(self):
        self.consumer.consumer_event += do_something
        self.assertEqual(self.consumer.consumer_event.subscriber_callbacks[0], do_something)

    def test_invoke_event(self):
        self.consumer.consumer_event += do_something
        self.assertEqual(self.consumer.consumer_event.subscriber_callbacks[0], do_something)
        self.consumer.invoke_event('the sword')
        self.assertEqual(global_test_string, 'doing something with the sword ...')

    def test_unsubscribe_from_event(self):
        self.consumer.consumer_event += do_something
        self.assertEqual(self.consumer.consumer_event.subscriber_callbacks[0], do_something)
        self.consumer.consumer_event -= do_something
        self.assertEqual(len(self.consumer.consumer_event.subscriber_callbacks), 0)

    def unsubscribe_non_existing_subscriber(self):
        self.consumer.consumer_event -= do_something

    def test_raise_if_no_callback_to_unsubscribe(self):
        self.assertRaises(UnsubscribeError, self.unsubscribe_non_existing_subscriber)

    def remove_non_callable_callback(self):
        self.consumer.consumer_event -= 'cat'

    def test_raise_if_unsubscribing_non_callable_callback(self):
        self.assertRaises(CallbackNotCallableError, self.remove_non_callable_callback)


if __name__ == '__main__':
    unittest.main()
