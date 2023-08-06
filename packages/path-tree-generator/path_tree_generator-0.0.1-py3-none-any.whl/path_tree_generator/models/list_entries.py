import pathlib

from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel


class ListEntryType(Enum):
    dir = 'dir'
    file = 'file'
    link = 'link'


class ListEntry(BaseModel):
    class Config:
        smart_union = True

    entry_type: ListEntryType
    name: str
    path: Union[str, pathlib.Path]
    size_bytes: Optional[int]
    children: Optional[list['ListEntry']]
    # @todo: add permissions and attributes like mod, own, grp, ...
