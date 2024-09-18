from samples.CardProbTable import CardProbTable
from samples.Card import Card, Pair
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