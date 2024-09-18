import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase
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

from typing import List, Literal, Union
from copy import deepcopy
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


class Observation:
    GameStates = Literal['discard','discard-pick','draw','draw-pick','koikoi']
    _observation: dict
    _hold: Union[Card,None]
    _pick: Union[Card,None]
    _myHands: List[Card]
    _boards: List[Card]
    _myObtaineds: List[Card]
    _opObtaineds: List[Card]
    _unknowns: List[Card]
    def __init__(self, observation):
        self._observation = observation
        if self.state in ('draw-pick', 'discard-pick'):
            self._hold = Card(*observation['show'][0])
        else:
            self._hold = None
        self._pick = None
        self._myHands = toCardList(self._observation['your_hand'])
        self._boards = toCardList(self._observation['field'])
        self._myObtaineds = unique(toCardList(
            self._observation['your_Light']
            + self._observation['your_Seed']
            + self._observation['your_Ribbon']
            + self._observation['your_Dross']
        ))
        self._opObtaineds = toCardList(self._observation['op_pile'])
    def getHoldables(self):
        if self.state in ('draw-pick', 'discard-pick'):
            return [self._hold]
        elif self.state in ('discard'):
            return self.myHands
        else:
            return []
    def getPickables(self, hold:Union[Card,None] =None):
        if hold == None:
            if self._hold == None:
                return []
            else:
                return [c for c in self.boards if c.month == self._hold.month]
        else:
            return [c for c in self.boards if c.month == hold.month]
    def getHoldPickPairs(self) -> List[Pair]:
        holdables = self.getHoldables()
        res: List[Pair] = []
        for hold in holdables:
            for pick in self.getPickables(hold=hold):
                res.append(Pair(hold=hold, pick=pick, month=hold.month))
            res.append(Pair(hold=hold, pick=None, month=hold.month))
        return res
    def holdUp(self, card:Card):
        if card in self.getHoldables():
            self._hold = card
        else:
            raise Exception('illegal action occured')
    def pickUp(self, card:Union[Card, None]):
        if card in self.getPickables() or card == None:
            self._pick = card
        else:
            raise Exception('illegal action occured')
    def applyHoldPickPair(self, pair:Pair):
        self.holdUp(pair.hold)
        self.pickUp(pair.pick)
    @property
    def ownTotalPoint(self): return self._observation['your_total_point']
    @property
    def opTotalPoint(self): return self._observation['op_total_point']
    @property
    def state(self)->GameStates: return self._observation['state']
    @property
    def hold(self): return self._hold
    @property
    def pick(self): return self._pick
    @property
    def myHands(self): return deepcopy(unique(self._myHands + [] if self._hold == None else [self._hold]))
    @property
    def boards(self): return deepcopy(unique(self._boards + [] if self._pick == None else [self._pick]))
    @property
    def myObtaineds(self): return deepcopy(self._myObtaineds)
    @property
    def opObtaineds(self): return deepcopy(self._opObtaineds)
    @property
    def unknowns(self):
        cardset = getCardSet()
        for c in self.myHands + self.boards + self.myObtaineds + self.opObtaineds:
            if c in cardset: cardset.remove(c)
        return cardset
    def __str__(self):
        return \
f"""
================
state:{self.state},
myHand:{self.myHands} ,myObtained: {self.myObtaineds}, pick: {self.pick}, hold: {self.hold}
board: {self.boards}, opObtained: {self.opObtaineds}
unknowns: {self.unknowns}
----------------
AllPossibleHoldPickPairs: {self.getHoldPickPairs()}
================
"""

from typing import List, Tuple, Dict

class CardProbTable:
    observation: Observation
    ownObtainRateTable: Dict[Card, float]
    opObtainRateTable: Dict[Card, float]
    def __init__(self,observation: Observation):
        self.observation = observation
        self.ownObtainRateTable = { c: 0.0 for c in getCardSet() }
        self.opObtainRateTable =  { c: 0.0 for c in getCardSet() }
        for m in range(1,12+1): self.updateProbTableFor(m)
    def getHoldPickPairs(self): return self.observation.getHoldPickPairs()
    def applyHoldPickPair(self, pair:Pair):
        holded_month = None
        if self.observation.hold != None:
            holded_month = self.observation.hold.month
        self.observation.applyHoldPickPair(pair)
        self.updateProbTableFor(pair.month)
        self.updateProbTableFor(holded_month)
    def mstateFor(self, month):
        m_state = [0,0,0,0,0]
        for c in cardsFor(month):
            if c in self.observation.myHands: m_state[0] += 1
            elif c in self.observation.boards: m_state[1] += 1
            elif c in self.observation.myObtaineds: m_state[2] += 1
            elif c in self.observation.unknowns: m_state[3] += 1
            elif c in self.observation.opObtaineds: m_state[4] += 1
        return tuple(m_state)
    def updateProbTableFor(self, month: int):
        # 怒涛のハードコード
        m_state = self.mstateFor(month)
        if  m_state == (2, 0, 0, 2, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 0.45357264829215155
                self.opObtainRateTable[card]  = 0.21309401837451517
        elif m_state == (0, 1, 2, 1, 0):
            for card in cardsFor(month):
                if card in self.observation.myObtaineds:
                    self.ownObtainRateTable[card] = 1.0
                    self.opObtainRateTable[card]  = 0.0
                else:
                    self.ownObtainRateTable[card] = 0.27208588957055213
                    self.opObtainRateTable[card]  = 0.7279141104294479
        elif m_state == (3, 1, 0, 0, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 1.0
                self.opObtainRateTable[card]  = 0.0
        elif m_state == (2, 0, 2, 0, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 1.0
                self.opObtainRateTable[card]  = 0.0
        elif m_state == (0, 1, 0, 1, 2):
            for card in cardsFor(month):
                if card in self.observation.opObtaineds:
                    self.ownObtainRateTable[card] = 0.0
                    self.opObtainRateTable[card]  = 1.0
                else:
                    self.ownObtainRateTable[card] = 0.3378726536621273
                    self.opObtainRateTable[card]  = 0.6621273463378726
        elif m_state == (1, 0, 0, 3, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 0.35792053127308526
                self.opObtainRateTable[card]  = 0.3087461353935814
        elif m_state == (0, 0, 2, 2, 0):
            for card in cardsFor(month):
                if card in self.observation.myObtaineds:
                    self.ownObtainRateTable[card] = 1.0
                    self.opObtainRateTable[card]  = 0.0
                else:
                    self.ownObtainRateTable[card] = 0.2677608248519451
                    self.opObtainRateTable[card]  = 0.7322391751480549
        elif m_state == (0, 0, 0, 4, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 0.1861675039808919
                self.opObtainRateTable[card]  = 0.48049916268577464
        elif m_state == (2, 0, 0, 0, 2):
            for card in cardsFor(month):
                if card in self.observation.myHands:
                    self.ownObtainRateTable[card] = 1.0
                    self.opObtainRateTable[card]  = 0.0
                else:
                    self.ownObtainRateTable[card] = 0.0
                    self.opObtainRateTable[card]  = 1.0
        elif m_state == (3, 0, 0, 1, 0):
            if self.observation.hold in cardsFor(month):
                for card in cardsFor(month):
                    if card in self.observation.myHands and card != self.observation.hold:
                        self.ownObtainRateTable[card] = 1.0
                        self.opObtainRateTable[card]  = 0.0
                    else:
                        self.ownObtainRateTable[card] = 0.6522756129287073
                        self.opObtainRateTable[card]  = 0.3477243870712926
            else:
                for card in cardsFor(month):
                    if card in self.observation.myHands:
                        self.ownObtainRateTable[card] = 0.8840918709762358
                        self.opObtainRateTable[card]  = 0.1159081290237642
                    else:
                        self.ownObtainRateTable[card] = 0.6522756129287073
                        self.opObtainRateTable[card]  = 0.3477243870712926
        elif m_state == (1, 1, 0, 2, 0):
            if self.observation.hold in cardsFor(month):
                for card in cardsFor(month):
                    if card in self.observation.myHands or card in self.observation.boards:
                        self.ownObtainRateTable[card] = 1.0
                        self.opObtainRateTable[card]  = 0.0
                    else:
                        self.ownObtainRateTable[card] = 0.2677608248519451
                        self.opObtainRateTable[card]  = 0.7322391751480549
            else:
                for card in cardsFor(month):
                    self.ownObtainRateTable[card] = 0.3672518987681677
                    self.opObtainRateTable[card]  = 0.2994147678984989
        elif m_state == (2, 2, 0, 0, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 1.0
                self.opObtainRateTable[card]  = 0.0
        elif m_state == (0, 0, 2, 0, 2):
            for card in cardsFor(month):
                if card in self.observation.myObtaineds:
                    self.ownObtainRateTable[card] = 1.0
                    self.opObtainRateTable[card]  = 0.0
                else:
                    self.ownObtainRateTable[card] = 0.0
                    self.opObtainRateTable[card]  = 1.0
        elif m_state == (0, 0, 0, 2, 2):
            for card in cardsFor(month):
                if card in self.observation.opObtaineds:
                    self.ownObtainRateTable[card] = 0.0
                    self.opObtainRateTable[card]  = 1.0
                else:
                    self.ownObtainRateTable[card] = 0.33479308520426937
                    self.opObtainRateTable[card]  = 0.6652069147957306
        elif m_state == (1, 3, 0, 0, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 1.0
                self.opObtainRateTable[card]  = 0.0
        elif m_state == (1, 0, 0, 1, 2):
            for card in cardsFor(month):
                if card in self.observation.opObtaineds:
                    self.ownObtainRateTable[card] = 0.0
                    self.opObtainRateTable[card]  = 1.0
                else:
                    self.ownObtainRateTable[card] = 0.6726046223786418
                    self.opObtainRateTable[card]  = 0.32739537762135806
        elif m_state == (1, 1, 2, 0, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 1.0
                self.opObtainRateTable[card]  = 0.0
        elif m_state == (1, 1, 0, 0, 2):
            for card in cardsFor(month):
                if card in self.observation.myHands or card in self.observation.boards:
                    self.ownObtainRateTable[card] = 1.0
                    self.opObtainRateTable[card]  = 0.0
                else:
                    self.ownObtainRateTable[card] = 0.0
                    self.opObtainRateTable[card]  = 1.0
        elif m_state == (0, 2, 0, 2, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 0.19892253086676845
                self.opObtainRateTable[card]  = 0.4677441357998982
        elif m_state == (1, 2, 0, 1, 0):
            if self.observation.hold in cardsFor(month):
                for card in cardsFor(month):
                    if card in self.observation.myHands or card == self.observation.pick:
                        self.ownObtainRateTable[card] = 1.0
                        self.opObtainRateTable[card]  = 0.0
                    else:
                        self.ownObtainRateTable[card] = 0.27208588957055213
                        self.opObtainRateTable[card]  = 0.7279141104294479
            else:
                for card in cardsFor(month):
                    if card in self.observation.myHands:
                        self.ownObtainRateTable[card] = 1.0
                        self.opObtainRateTable[card]  = 0.0
                    else:
                        self.ownObtainRateTable[card] = 0.26882163144739835
                        self.opObtainRateTable[card]  = 0.7311783685526017
        elif m_state == (0, 0, 4, 0, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 1.0
                self.opObtainRateTable[card]  = 0.0
        elif m_state == (0, 3, 0, 1, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 0.30808080808080807
                self.opObtainRateTable[card]  = 0.6919191919191919
        elif m_state == (0, 0, 0, 0, 4):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 0.0
                self.opObtainRateTable[card]  = 1.0
        elif m_state == (1, 0, 2, 1, 0):
            for card in cardsFor(month):
                if card in self.observation.myObtaineds:
                    self.ownObtainRateTable[card] = 1.0
                    self.opObtainRateTable[card]  = 0.0
                else:
                    self.ownObtainRateTable[card] = 0.6563044715704256
                    self.opObtainRateTable[card]  = 0.34369552842957435
        elif m_state == (0, 1, 0, 3, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 0.1874217172531972
                self.opObtainRateTable[card]  = 0.47924494941346946
        elif m_state == (2, 1, 0, 1, 0):
            if self.observation.hold in cardsFor(month):
                for card in cardsFor(month):
                    if card == self.observation.hold or card in self.observation.boards:
                        self.ownObtainRateTable[card] = 1.0
                        self.opObtainRateTable[card]  = 0.0
                    else:
                        self.ownObtainRateTable[card] = 0.6563044715704256
                        self.opObtainRateTable[card]  = 0.34369552842957435
            else:
                for card in cardsFor(month):
                    self.ownObtainRateTable[card] = 0.5608369778099601
                    self.opObtainRateTable[card]  = 0.4391630221900399
        elif m_state == (4, 0, 0, 0, 0):
            for card in cardsFor(month):
                self.ownObtainRateTable[card] = 1.0
                self.opObtainRateTable[card]  = 0.0
    def __getitem__(self, own:Literal['own', 'op'], card:Card):
        if own == 'own':
            return self.ownObtainRateTable[card]
        else:
            return self.opObtainRateTable[card]

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

from typing import Literal, NamedTuple, Union, List

class Evaluation(NamedTuple):
    distance: Union[float, None]
    possibility: Literal['IMPOSSIBLE', 'POSSIBLE', 'ALREADY']

TANE_CARDS = [Card(2,1),Card(4,1),Card(5,1),Card(6,1),Card(7,1),Card(8,2),Card(9,1),Card(10,1),Card(11,2)]
TAN_CARDS = [Card(1,2),Card(2,2),Card(3,2),Card(4,2),Card(5,2),Card(6,2),Card(7,2),Card(9,2),Card(10,2),Card(11,3)]
KASU_CARDS = [
    Card(1,3),Card(1,4),Card(2,3),Card(2,4),Card(3,3),Card(3,4),
    Card(4,3),Card(4,4),Card(5,3),Card(5,4),Card(6,3),Card(6,4),
    Card(7,3),Card(7,4),Card(8,3),Card(8,4),Card(9,3),Card(9,4),
    Card(10,3),Card(10,4),
    Card(11,4),Card(12,2),Card(12,3),Card(12,4),Card(9,1)
]

def contains_tane(pair:Pair):
    if pair.pick in TANE_CARDS and pair.hold in TANE_CARDS: return 2
    elif pair.pick in TANE_CARDS: return 1
    elif pair.hold in TANE_CARDS: return 1
    else: return 0
def contains_tann(pair:Pair):
    if pair.pick in TAN_CARDS and pair.hold in TAN_CARDS: return 2
    elif pair.pick in TAN_CARDS: return 1
    elif pair.hold in TAN_CARDS: return 1
    else: return 0
def contains_kasu(pair:Pair):
    if pair.pick in KASU_CARDS and pair.hold in KASU_CARDS: return 2
    elif pair.pick in KASU_CARDS: return 1
    elif pair.hold in KASU_CARDS: return 1
    else: return 0

class RoleProbTable:
    cardProbTable: CardProbTable
    def __init__(self, cardProbTable:CardProbTable):
        self.cardProbTable = cardProbTable
    def distanceToNecessaryCards(self, own: Literal['own', 'op'], cards: List[Card]):
        distance = 0
        haveAll = True
        for c in cards:
            if self.cardProbTable[own, c] != 1.0:
                haveAll = False
            if self.cardProbTable[own, c] == 0.0:
                return Evaluation(None, 'IMPOSSIBLE')
            distance += 1-self.cardProbTable[own, c]
        if haveAll:
            return Evaluation(0.0, 'ALREADY')
        return Evaluation(distance, 'POSSIBLE')
    def distanceToClosestCards(self, own: Literal['own', 'op'], cards: List[Card], number: int):
        grossDistance = 0
        distances = sorted([1-self.cardProbTable[own, c] for c in cards])
        for d in distances[0:number]:
            if d == 1.0:
                return Evaluation(None, 'IMPOSSIBLE')
            grossDistance += d
        if grossDistance == 0.0:
            return Evaluation(distances[number], 'ALREADY')
        return Evaluation(grossDistance, 'POSSIBLE')
    def allEvaluations(self, own: Literal['own', 'op']):
        return [
            self.evaluateFiveLights(own),
            self.evaluateFourLights(own),
            self.evaluateRainyFourLights(own),
            self.evaluateThreeLights(own),
            self.evaluateBoarDeerButterfly(own),
            self.evaluateFlowerViewingSake(own),
            self.evaluateMoonViewingSake(own),
            self.evaluateRedRibbons(own),
            self.evaluateBlueRibbons(own),
            self.evaluateKasu(own),
            self.evaluateTan(own),
            self.evaluateTane(own)
        ]
    def minimumDistance(self, own: Literal['own', 'op']):
        evaluations = self.allEvaluations(own)
        minimum = None
        for ev in evaluations:
            if ev.possibility == 'POSSIBLE': 
                if minimum == None: minimum = ev.distance
                else: minimum = min(minimum, ev.distance)
        return minimum
    def grossDistance(self, own: Literal['own', 'op']):
        evaluations = self.allEvaluations(own)
        gross = 0
        for ev in evaluations:
            if ev.possibility == 'POSSIBLE':
                gross += ev.distance
        return gross
    def evaluateFiveLights(self, own: Literal['own', 'op']):
        return self.distanceToNecessaryCards(own, [Card(1,1),Card(3,1),Card(8,1),Card(11,1),Card(12,1)])
    def evaluateFourLights(self, own: Literal['own', 'op']):
        return self.distanceToNecessaryCards(own, [Card(1,1),Card(3,1),Card(8,1),Card(12,1)])
    def evaluateRainyFourLights(self, own: Literal['own', 'op']):
        rain = self.distanceToNecessaryCards(own, [Card(11,1)])
        other3 = self.distanceToClosestCards(own, [Card(1,1),Card(3,1),Card(8,1),Card(12,1)], 3)
        if rain.possibility == 'IMPOSSIBLE' or other3.possibility == 'IMPOSSIBLE':
            return Evaluation(None, 'IMPOSSIBLE')
        if rain.possibility == 'ALREADY' and other3.possibility == 'ALREADY':
            return Evaluation(other3.distance, 'ALREADY')
        return Evaluation(rain.distance + other3.distance, 'POSSIBLE')
    def evaluateThreeLights(self, own: Literal['own', 'op']):
        return self.distanceToClosestCards(own, [Card(1,1), Card(3,1), Card(8,1), Card(12,1)], 3)
    def evaluateBoarDeerButterfly(self, own: Literal['own', 'op']):
        return self.distanceToNecessaryCards(own, [Card(6,1), Card(7,1), Card(10,1)])
    def evaluateFlowerViewingSake(self, own: Literal['own', 'op']):
        return self.distanceToNecessaryCards(own, [Card(9,1), Card(3,1)])
    def evaluateMoonViewingSake(self, own: Literal['own', 'op']):
        return self.distanceToNecessaryCards(own, [Card(9,1), Card(8,1)])
    def evaluateRedRibbons(self, own: Literal['own', 'op']):
        return self.distanceToNecessaryCards(own, [Card(1,2), Card(2,2), Card(3,2)])
    def evaluateBlueRibbons(self, own: Literal['own', 'op']):
        return self.distanceToNecessaryCards(own, [Card(6,2), Card(9,2), Card(10,2)])
    def evaluateTane(self, own: Literal['own', 'op']):
        return self.distanceToClosestCards(own, TANE_CARDS, 5)
    def evaluateTan(self, own: Literal['own', 'op']):
        return self.distanceToClosestCards(own, TAN_CARDS, 5)
    def evaluateKasu(self, own: Literal['own', 'op']):
        return self.distanceToClosestCards(own, KASU_CARDS, 10)

from typing import NamedTuple, List

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．

with open('log2','a') as f:
    f.write('Agent loaded\n')

class Score(NamedTuple):
    acm_score: float
    opClosestRoleDistance: float
    ownGrossRoleDistance: float
    pair: Pair
    def __lt__(self, other):
        # sortの都合上都合が良い方にTrueを返す
        if self.opClosestRoleDistance - other.opClosestRoleDistance < 0.1: return False #selfが大きいほうが都合が良い
        elif self.opClosestRoleDistance - other.opClosestRoleDistance > 0.1: return True
        elif self.ownGrossRoleDistance - other.ownGrossRoleDistance < 0.1: return True #selfが小さいほうが都合が良い
        elif self.ownGrossRoleDistance - other.ownGrossRoleDistance > 0.1: return False
        elif self.acm_score > other.acm_score: return True #selfが大きいほうが都合が良い
        else: return False

class MyAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()
    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        # ランダムに取れる行動をする
        if observation['legal_action'] == [None]:
            return None
        _observation = Observation(observation)
        if _observation.state in ('discard','discard-pick','draw-pick'):
            cardProbTable = CardProbTable(_observation)
            roleProbTable = RoleProbTable(cardProbTable)
            scores:List[Score] = []
            for pair in cardProbTable.getHoldPickPairs():
                cardProbTable.applyHoldPickPair(pair)
                number_of_tane = contains_tane(pair)
                number_of_kasu = contains_kasu(pair)
                number_of_tann = contains_tann(pair)
                acm_score = number_of_tane*(9/5)+number_of_kasu*(10/5)+number_of_tann*(25/10)
                opClosestRoleDistance = roleProbTable.minimumDistance('op')
                ownGrossRoleDistance = roleProbTable.grossDistance('own')
                scores.append(
                    Score(acm_score, opClosestRoleDistance, ownGrossRoleDistance, pair)
                )
            selected = sorted(scores)[0]
            if _observation.state == 'discard':
                return selected.pair.hold.asList()
            else:
                return selected.pair.pick.asList()
        elif _observation.state == 'koikoi':
            return _observation.opTotalPoint > _observation.ownTotalPoint

if __name__ == "__main__":
    my_agent = MyAgent()  # 参加者が実装したプレイヤーをインスタンス化

    mode = int(
        input(
            "Enter mode (1 for playing against AI, 2 for playing against another client): "
        )
    )
    num_games = int(input("Enter number of games to play: "))
    player_name = input("Enter your player name: ")

    sio_client = SocketIOClient(
        ip="localhost",
        port=5000,
        namespace="/koi-koi",
        agent=my_agent,
        room_id=123,
        player_name=player_name,
        mode=mode,
        num_games=num_games,
    )
    sio_client.run()
    # sio.client.enter_room()
