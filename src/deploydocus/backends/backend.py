import abc
from typing import Any


class StateDb:
    @abc.abstractmethod
    def create(self, manifest: Any): ...
