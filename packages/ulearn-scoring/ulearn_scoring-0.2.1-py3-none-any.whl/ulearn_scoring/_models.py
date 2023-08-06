from decimal import Decimal
from typing import NamedTuple


class StudentScores(NamedTuple):
    student: str
    scores: Decimal
