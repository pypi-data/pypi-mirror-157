from typing import *
from .components.base_component import BaseComponent



class IDSchema():
    Components: List[BaseComponent] = list()

    @classmethod
    def generate_n(cls, n: int) -> List[str]:
        return [cls.generate_one() for _ in range(n)]
        
    @classmethod
    def generate_n_unique(cls, n: int, max_retry: int = 20) -> List[str]:
        ids = list()
        while len(ids) < n:
            new_id = cls.generate_one()
            if new_id in ids:
                max_retry -= 1
                if max_retry == 0:
                    raise RuntimeError(f"Max Retry exceeded trying to generate {n!s} unique ids.")
                continue
            ids.append(new_id)
        return ids

    @classmethod
    def generate_one(cls) -> str:
        id_ = ""
        for component in cls.Components:
            id_ += component.generate()
        return id_

    @classmethod
    def validate(cls, id_ : str, start_component_index: int = 0) -> bool:
        if start_component_index == len(cls.Components):
            return id_ == ""
        sub_ids = cls.Components[start_component_index].reduce_all_matching(id_)
        for sub_id in sub_ids:
            if cls.validate(sub_id, start_component_index+1):
                return True
        return False

        