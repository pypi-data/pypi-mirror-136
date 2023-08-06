from decimal import Decimal
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import FilePath
from pydantic import Field
from pydantic_yaml import VersionedYamlModel

from ._common import ALL_MODULES
from ._typing import Modules


class Statement(BaseModel):
    file: FilePath
    modules: Modules = ALL_MODULES


class FinalStatement(Statement):
    scoring_ratio: Decimal = Field(default=Decimal('0.5'), ge=0, le=1)


class StatementsConfig(VersionedYamlModel):
    statements: List[Statement]
    final_statement: Optional[FinalStatement] = None

    class Config:
        min_version = '1.0.0'
        max_version = '2.0.0'
