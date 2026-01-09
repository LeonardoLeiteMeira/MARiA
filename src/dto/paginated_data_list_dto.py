from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedDataListDto(BaseModel, Generic[T]):
    list_data: list[T]
    page: int
    page_size: int
    total_count: int

    model_config = ConfigDict(from_attributes=True)
