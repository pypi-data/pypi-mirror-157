from typing import *
from .base_component import BaseComponent
import random
import collections

class LengthRange:
    def __init__(self, min_length: int, max_length: Optional[int] = None):
        self.min = min_length
        self.max = max_length if max_length is not None else min_length
        self._validate_range()
        
    def _validate_range(self) -> None:
        if self.min > self.max:
            raise ValueError("Constraint failed: min <= max.")

    def one_in_range(self) -> int:
        return random.randint(self.min, self.max)

    def __contains__(self, number: int) -> bool:
        return self.min <= number <= self.max

    def __iter__(self):
        return iter(range(self.min, self.max+1))


class RandomGroup(BaseComponent):
    def __init__(self, alphabet: Sequence[str], length: Union[LengthRange,Sequence[int],int,None] = None, alphabet_weights: Optional[Sequence[float]] = None, unique: bool=False) -> None:
        self.alphabet = alphabet
        self.length_range = self._create_length_range(length)
        self.alphabet_weights = alphabet_weights
        self.unique = unique


    def _create_length_range(self, length: Union[LengthRange,Sequence[int],int,None]) -> LengthRange:
        if length is None:
            return LengthRange(len(self.alphabet))
        if isinstance(length, int):
            return LengthRange(length)
        if isinstance(length, collections.abc.Sequence):
            if len(length) != 2:
                raise ValueError("length of 'length' has to be 2.")
            return LengthRange(length[0], length[1])
        if isinstance(length, LengthRange):
            return length
        raise TypeError("type of 'length' has to be one of ('LengthRange', 'collections.Sequence', 'int').")

    def generate(self) -> str:
        if self.unique:
            return "".join(random.sample(self.alphabet, self.length_range.one_in_range()))
        return "".join(random.choices(self.alphabet, weights=self.alphabet_weights, k=self.length_range.one_in_range()))


    def validate(self, group: Sequence[str]) -> bool:
        if len(group) not in self.length_range:
            return False

        if self.unique and len(set(group)) != len(group):
            return False

        return all(map(lambda x: x in self.alphabet, group))

    def reduce_all_matching(self, sub_id: str) -> Iterator[str]:
        for i in self.length_range:
            if self.validate(sub_id[:i]):
                yield sub_id[i:]
