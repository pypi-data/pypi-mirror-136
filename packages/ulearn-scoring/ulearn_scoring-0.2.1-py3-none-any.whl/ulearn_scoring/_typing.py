import sys
from typing import Union
from typing import Sequence

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


Modules = Union[Sequence[str], Literal['*']]
