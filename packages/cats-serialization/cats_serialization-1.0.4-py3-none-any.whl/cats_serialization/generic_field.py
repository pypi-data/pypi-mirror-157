from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

T = TypeVar('T')


class GenericField(ABC, Generic[T]):

    @abstractmethod
    def serialize(self, data_object: T, key: str | None = None) -> Any:
        pass
