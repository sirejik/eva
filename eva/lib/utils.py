import logging
import os
import sys
import time

from eva.lib.settings import TIME_INTERVAL_BETWEEN_ATTEMPTS, LOG_FILE_NAME

logger = logging.getLogger()


class FunctionResultWaiter(object):
    """
    This class is used for subsequent invoking of the function until it returns the expected result. Otherwise, an error
    will be thrown.
    """
    def __init__(self, func, error, **kwargs):
        """
        - func: the function that is called multiple times
        - error: the error that is thrown if the function was not executed successfully at least once
        - expected_result: if this is set, then the execution is considered successful if it returns the
            expected_result.
        - check_function: if expected_result is specified, then successful execution of check_function means that the
            function was executed successfully. If expected_result and check_function are not specified, then the
            execution will be considered successful if the result is not None.
        - max_attempts: the maximum number of attempts, for unlimited attempts pass 0 or -1 here
        - interval_between_attempts: the interval between attempts
        - throw_exception_on_failure: Should an exception be thrown on failure
        """
        expected_result = kwargs.get('expected_result', None)
        if expected_result is not None:
            self._check_function = lambda x: x == expected_result
        else:
            self._check_function = kwargs.get('check_function', lambda x: x is not None)

        self._func = func
        self._error = error

        self._max_attempts = kwargs.get('max_attempts', 0)
        self._interval_between_attempts = kwargs.get('interval_between_attempts', TIME_INTERVAL_BETWEEN_ATTEMPTS)
        self._throw_exception_on_failure = kwargs.get('throw_exception_on_failure', True)

    def _is_unlimited_attempts(self):
        return self._max_attempts <= 0

    def run(self, *args, **kwargs):
        """
        Executing the specified function max_attempts times once in interval_between_attempts seconds. If the function
        did not return the necessary result at least once, then throw the specified error. The arguments args, *kwargs
        are the arguments for the function being executed.
        """
        attempt = 0
        while attempt < self._max_attempts or self._is_unlimited_attempts():
            result = self._func(*args, **kwargs)
            if self._check_function(result):
                return result

            attempt += 1
            time.sleep(self._interval_between_attempts)

        if self._throw_exception_on_failure:
            raise self._error


def configure_logging():
    dirname = os.path.dirname(LOG_FILE_NAME)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')
    stdout_logger_handler = logging.StreamHandler(sys.stdout)
    stdout_logger_handler.setLevel(logging.INFO)
    stdout_logger_handler.setFormatter(formatter)
    logger.addHandler(stdout_logger_handler)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')
    file_logger_handler = logging.FileHandler(LOG_FILE_NAME)
    file_logger_handler.setLevel(logging.NOTSET)
    file_logger_handler.setFormatter(formatter)
    logger.addHandler(file_logger_handler)
