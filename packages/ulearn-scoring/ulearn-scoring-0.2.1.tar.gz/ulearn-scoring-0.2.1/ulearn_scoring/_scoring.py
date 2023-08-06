import pathlib
from typing import Callable
from typing import Iterable

from ._config import StatementsConfig
from ._config import FinalStatement
from ._storages import AbstractStudentScoresStorage
from ._writers import AbstractScoresWriter
from ._readers import AbstractScoresReader
from ._models import StudentScores


class ScoringService:
    def __init__(
        self,
        scores_storage_factory: Callable[[], AbstractStudentScoresStorage],
        scores_writer_factory: Callable[[], AbstractScoresWriter],
        scores_reader_factory: Callable[[], AbstractScoresReader],
    ):
        self._scores_storage_factory = scores_storage_factory
        self._scores_writer_factory = scores_writer_factory
        self._scores_reader_factory = scores_reader_factory

    def score(self, config: StatementsConfig, result_file: pathlib.Path) -> None:
        storage = self._scores_storage_factory()
        reader = self._scores_reader_factory()
        writer = self._scores_writer_factory()

        for statement in config.statements:
            for scores in reader.read(statement.file, statement.modules):
                storage.add_scores(scores.student, scores.scores)

        if config.final_statement is not None:
            final_scores_iter = self._scores_final_statement(
                final_statement=config.final_statement,
                scores_reader=reader,
                scores_storage=storage,
            )
            for scores in final_scores_iter:
                storage.add_scores(scores.student, scores.scores)

        writer.write(result_file, storage.get_all_scores())

    @staticmethod
    def _scores_final_statement(
        final_statement: FinalStatement,
        scores_reader: AbstractScoresReader,
        scores_storage: AbstractStudentScoresStorage
    ) -> Iterable[StudentScores]:
        final_scores = {}
        student_scores_iter = scores_reader.read(
            file=final_statement.file,
            modules=final_statement.modules,
        )

        for scores in student_scores_iter:
            final_scores[scores.student] = scores.scores

        for scores in scores_storage.get_all_scores():
            if scores.student not in final_scores:
                continue

            scores_diff = (final_scores[scores.student] - scores.scores) * final_statement.scoring_ratio
            final_scores[scores.student] = scores_diff

        for student, scores in final_scores.items():
            yield StudentScores(student, scores)
