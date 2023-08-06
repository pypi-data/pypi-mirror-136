"""
    @Time    : 11.12.2021 19:44
    @Author  : Subvael
    @File    : exceptions.py
"""


class AirignisError(Exception):
    """Base class for airignis exceptions
    """

    def __init__(self, *args):
        self.error_msg = 'Base airignis exception'
        self.set_valid_custom_message(*args)
        super().__init__(self.error_msg)

    def set_valid_custom_message(self, *args):
        """This function allows overwriting standard error messages with custom messages

        :param args: Arguments to be notified when raising the exception
        """
        if len(args) != 0 and hasattr(args[0], '__str__'):
            self.error_msg = args[0]


class UndefinedRateUnitError(AirignisError):
    """Raised when setting an unknown rate unit for a DueTime object
    """

    def __init__(self, *args):
        self.error_msg = 'An invalid rate unit was passed'
        self.set_valid_custom_message(*args)
        super().__init__(self.error_msg, *args)


class DateNotConfiguredError(AirignisError):
    """Raised when trying to get the non-configured and optional date of a DueTime
    """

    def __init__(self, *args):
        self.error_msg = 'The date attribute was not configured'
        self.set_valid_custom_message(*args)
        super().__init__(self.error_msg, *args)


class CallbackNotCallableError(AirignisError):
    """Raised when trying to set a non-callable object as callback
    """

    def __init__(self, *args):
        self.error_msg = 'A non callable item was added as subscriber\'s callback function'
        self.set_valid_custom_message(*args)
        super().__init__(self.error_msg, *args)


class UnsubscribeError(AirignisError):
    """Raised when trying to unsubscribe a non-existing subscriber
    """

    def __init__(self, *args):
        self.error_msg = 'Trying to unsubscribe a non existing subscriber'
        self.set_valid_custom_message(*args)
        super().__init__(self.error_msg, *args)


if __name__ == '__main__':
    pass
