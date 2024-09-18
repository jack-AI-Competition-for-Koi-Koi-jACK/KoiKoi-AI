from samples.Card import *
from samples.Observation import *
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