from abc import ABCMeta, abstractmethod

from uws.models import Job


class Worker(metaclass=ABCMeta):
    """Abstract Worker class"""

    def __init__(self):
        self._type = None

    @abstractmethod
    def run(self, job: Job) -> None:
        pass

    @property
    def type(self):
        return self._type
