from typing import List, TypeVar, Generic

from pydantic import BaseModel
from pydantic.generics import GenericModel


class PageRequest(BaseModel):
    page: int
    size: int


ItemT = TypeVar("ItemT")


class Page(GenericModel, Generic[ItemT]):
    items: List[ItemT]
    page: int
    size: int
    total: int
