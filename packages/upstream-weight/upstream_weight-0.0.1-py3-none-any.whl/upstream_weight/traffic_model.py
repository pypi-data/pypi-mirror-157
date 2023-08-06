from typing import Dict, List

from pydantic import BaseModel

__all__ = ['Traffic', 'TrafficItem']


class TrafficItem(BaseModel):
    category: str = None
    ratio: int = 0
    count: int
    weight: int = 0


class Traffic(BaseModel):
    __root__: Dict[str, TrafficItem]

    def items(self):
        return self.__root__.items()

    def values(self):
        return self.__root__.values()

    def data(self):
        return self.dict()['__root__']

    def item_list(self) -> List[TrafficItem]:
        res = []
        for name, value in self.__root__.items():
            value.category = name
            res.append(value)

        return res

    def __getattr__(self, item):
        return self.__root__[item]
