import os
import typing

Slice = typing.TypeVar('Slice', bound=typing.Sequence)
FilePath = typing.Union[str, bytes, os.PathLike]
