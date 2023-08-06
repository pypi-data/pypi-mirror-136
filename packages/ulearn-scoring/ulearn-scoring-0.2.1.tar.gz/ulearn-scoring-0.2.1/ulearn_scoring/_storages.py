from abc import ABCMeta
from abc import abstractmethod
from decimal import Decimal
from collections import Counter
from typing import Iterable

from ._models import StudentScores


class AbstractStudentScoresStorage(metaclass=ABCMeta):
    @abstractmethod
    def add_scores(self, student: str, score: Decimal = Decimal(1)) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_all_scores(self) -> Iterable[StudentScores]:
        raise NotImplementedError()


class StudentScoresStorage(AbstractStudentScoresStorage):
    def __init__(self):
        self._scores_storage = Counter()

    def add_scores(self, student: str, score: Decimal = Decimal(1)) -> None:
        self._scores_storage[student] += score

    def get_all_scores(self) -> Iterable[StudentScores]:
        yield from map(lambda item: StudentScores(*item), self._scores_storage.items())
