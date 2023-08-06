import sys
import pathlib
from typing import cast

import click
from pydantic import ValidationError

from ._di import create_container
from ._scoring import ScoringService
from ._config import StatementsConfig


@click.command()
@click.version_option()
@click.option(
    '-c', '--config', 'config',
    type=click.Path(exists=True),
    help='Config for scoring',
    envvar='SCORING_CONFIG',
)
@click.option(
    '-o', '--output', 'output',
    type=click.Path(exists=False),
    help='Result file',
    envvar='SCORING_RESULT_FILE',
)
def cli(config: str, output: str):
    """Scoring of statements in ulearn by weeks"""
    click.echo('[X] Prepare tool')

    di_container = create_container()

    service = cast(
        ScoringService,
        di_container.resolve(ScoringService),
    )
    try:
        config = StatementsConfig.parse_file(config)
    except ValidationError as e:
        click.echo(f'[X] Config format error: {e}')
        sys.exit(1)

    click.echo('[X] Start scoring')

    try:
        service.score(
            config=config,
            result_file=pathlib.Path(output),
        )
    except Exception as e:
        click.echo(f'[X] Error: {e}')
        sys.exit(1)

    click.echo('[X] End scoring')
