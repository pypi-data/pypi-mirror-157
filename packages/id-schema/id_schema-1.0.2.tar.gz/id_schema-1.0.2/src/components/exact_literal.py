from typing import *
from .base_component import BaseComponent


class ExactLiteral(BaseComponent):
    def __init__(self, literal: str) -> None:
        self.literal = literal

    def generate(self) -> str:
        return self.literal
    
    def validate(self, literal: Sequence[str]) -> bool:
        return literal == self.literal

    def reduce_all_matching(self, sub_id: str) -> Iterator[str]:
        if sub_id.startswith(self.literal):
            yield sub_id[len(self.literal):]