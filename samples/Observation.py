from typing import List, Literal, Union
from copy import deepcopy
from samples.Card import *

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
