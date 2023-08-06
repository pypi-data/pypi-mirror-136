from typing import Callable

import punq

from ._storages import StudentScoresStorage
from ._storages import AbstractStudentScoresStorage
from ._writers import CsvScoresWriter
from ._writers import AbstractScoresWriter
from ._readers import AutoScoresReader
from ._readers import AbstractScoresReader
from ._scoring import ScoringService


def create_container() -> punq.Container:
    container = punq.Container()
    container.register(Callable[[], AbstractStudentScoresStorage], instance=StudentScoresStorage)
    container.register(Callable[[], AbstractScoresWriter], instance=CsvScoresWriter)
    container.register(Callable[[], AbstractScoresReader], instance=AutoScoresReader)
    container.register(ScoringService)

    return container
