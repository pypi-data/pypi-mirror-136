from abc import ABCMeta, abstractmethod
import logging
import functools
from typing import Type

import requests
from requests import Response


from io import StringIO
import sys


class Capturing(list):
    """More info: https://stackoverflow.com/a/16571630"""

    def __enter__(self) -> "Capturing":
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args) -> None:
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class BaseConnector(metaclass=ABCMeta):
    def __init__(self, url) -> None:
        self.url = url

    @abstractmethod
    def send_message(self, msg: str) -> Response:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class GChatConnector(BaseConnector):
    def send_message(self, msg: str) -> Response:
        return requests.post(self.url, json={"text": msg})


class LogShipper:
    def __init__(self, connector: Type[BaseConnector]) -> None:
        self.connector = connector

    def __call__(self, fn):
        """This is used for the decorator functionality"""

        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            print(f"In my decorator before call, with {self.connector}")
            with Capturing() as output:
                result = fn(*args, **kwargs)
            for output_line in output:
                self.log_print(output_line)
            print(f"In my decorator after call, with {self.connector}")
            return result

        return decorated

    def log_print(self, msg: str) -> None:
        print(f"Send message via {self.connector}: {msg}")
        self.send_message(msg)

    def send_message(self, msg: str) -> Response:
        return self.connector.send_message(msg)
