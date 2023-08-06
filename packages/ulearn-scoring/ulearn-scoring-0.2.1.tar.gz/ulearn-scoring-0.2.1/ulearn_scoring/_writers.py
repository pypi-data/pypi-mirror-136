import csv
import pathlib
from abc import ABCMeta
from abc import abstractmethod
from typing import Iterable

from ._models import StudentScores


class AbstractScoresWriter(metaclass=ABCMeta):
    @abstractmethod
    def write(
        self,
        file: pathlib.Path,
        student_scores: Iterable[StudentScores],
    ) -> None:
        raise NotImplementedError()


class CsvScoresWriter(AbstractScoresWriter):
    def write(
        self,
        file: pathlib.Path,
        student_scores: Iterable[StudentScores],
    ) -> None:
        with file.open('w') as csvfile:
            writer = csv.writer(csvfile)

            for scores in student_scores:
                writer.writerow(scores)
