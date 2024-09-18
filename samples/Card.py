from itertools import product
from typing import NamedTuple, List, Union

class Card(NamedTuple):
    month: int
    variant: int
    def __repr__(self):
        return f"({self.month},{self.variant})"
    def asList(self):
        return [self.month, self.variant]

def toCardList(obj: List[List[int]]):
    return list(set( # avoids duplication
        map(lambda card: Card(*card) ,obj) # castToCard
    ))

def unique(obj: List[Card]):
    return list(set(obj))

def getCardSet(): return [Card(m,k) for m,k in product(range(1,12+1),range(1,4+1))]

class Pair(NamedTuple):
    hold: Card
    pick: Union[Card,None]
    month: int
    def __repr__(self):
        return f"<{self.hold},{self.pick}>"

def cardsFor(month: int):
    return [Card(month,v) for v in range(1,4+1)]
