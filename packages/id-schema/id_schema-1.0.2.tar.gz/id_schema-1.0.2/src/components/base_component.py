from typing import *
import abc


class BaseComponent(abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def generate(self) -> str:
        ...

    @abc.abstractmethod
    def validate(self, sub_id: str) -> bool:
        ...

    @abc.abstractmethod
    def reduce_all_matching(self, sub_id: str) -> Iterator[str]:
        ...