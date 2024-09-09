import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase

from itertools import product
from copy import deepcopy

# 全札のリストを返す．
# (参照渡しによって，書き換えが思わぬ範囲に影響を及ぼすことを嫌ってファクトリ関数を作っている)
def card_set_factory(): return [[m,k] for m,k in product(range(1,12+1),range(1,4+1)) ] 

# M_STATE:
# 各月ごとに考える状態. 詳説すると，各5状態のその月の札が何枚あるかという数字の組．
# 各5状態とは 自身の手札，場札，自身の取札, 不明，相手の取札
# である．
# 例えば2月の札が2枚手札にあり，2枚が不明な場合， 2月のM_STATEは (2,0,0,2,0)

def make_m_states(myHand, board, myObtained, unknown, opObtained):
    m_states = {m:[0,0,0,0,0] for m in range(1,12+1)} # 各月がキー
    for c in myHand: m_states[c[0]][0] += 1
    for c in board: m_states[c[0]][1] += 1
    for c in myObtained: m_states[c[0]][2] += 1
    for c in unknown: m_states[c[0]][3] += 1
    for c in opObtained: m_states[c[0]][4] += 1
    return {m:tuple(m_states[m]) for m in m_states}

def calcObtainProb(
    myHand:List[List[int]], 
    board:List[List[int]], 
    myObtained:List[List[int]], 
    unknown:List[List[int]], 
    opObtained:List[List[int]], 
    hold:List[int], 
    pick:List[int]
):
    ownObtainRateTable = { c: 0.0 for c in card_set_factory() }
    opObtainRateTable =  { c: 0.0 for c in card_set_factory() }
    m_states = make_m_states(myHand, board, myObtained, unknown, opObtained)
    
    # 怒涛のハードコード
    for m in m_states:
        m_state = m_states[m]
        if   m_state == (2, 0, 0, 2, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 0.45357264829215155
                opObtainRateTable[card]  = 0.21309401837451517
        elif m_state == (0, 1, 2, 1, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in myObtained:
                    ownObtainRateTable[card] = 1.0
                    opObtainRateTable[card]  = 0.0
                else:
                    ownObtainRateTable[card] = 0.27208588957055213
                    opObtainRateTable[card]  = 0.7279141104294479
        elif m_state == (3, 1, 0, 0, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 1.0
                opObtainRateTable[card]  = 0.0
        elif m_state == (2, 0, 2, 0, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 1.0
                opObtainRateTable[card]  = 0.0
        elif m_state == (0, 1, 0, 1, 2):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in opObtained:
                    ownObtainRateTable[card] = 0.0
                    opObtainRateTable[card]  = 1.0
                else:
                    ownObtainRateTable[card] = 0.3378726536621273
                    opObtainRateTable[card]  = 0.6621273463378726
        elif m_state == (1, 0, 0, 3, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 0.35792053127308526
                opObtainRateTable[card]  = 0.3087461353935814
        elif m_state == (0, 0, 2, 2, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in myObtained:
                    ownObtainRateTable[card] = 1.0
                    opObtainRateTable[card]  = 0.0
                else:
                    ownObtainRateTable[card] = 0.2677608248519451
                    opObtainRateTable[card]  = 0.7322391751480549
        elif m_state == (0, 0, 0, 4, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 0.1861675039808919
                opObtainRateTable[card]  = 0.48049916268577464
        elif m_state == (2, 0, 0, 0, 2):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in myHand:
                    ownObtainRateTable[card] = 1.0
                    opObtainRateTable[card]  = 0.0
                else:
                    ownObtainRateTable[card] = 0.0
                    opObtainRateTable[card]  = 1.0
        elif m_state == (3, 0, 0, 1, 0):
            if hold in [[m,1],[m,2],[m,3],[m,4]]:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    if card in myHand and card != hold:
                        ownObtainRateTable[card] = 1.0
                        opObtainRateTable[card]  = 0.0
                    else:
                        ownObtainRateTable[card] = 0.6522756129287073
                        opObtainRateTable[card]  = 0.3477243870712926
            else:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    if card in myHand:
                        ownObtainRateTable[card] = 0.8840918709762358
                        opObtainRateTable[card]  = 0.1159081290237642
                    else:
                        ownObtainRateTable[card] = 0.6522756129287073
                        opObtainRateTable[card]  = 0.3477243870712926
        elif m_state == (1, 1, 0, 2, 0):
            if hold in [[m,1],[m,2],[m,3],[m,4]]:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    if card in myHand or card in board:
                        ownObtainRateTable[card] = 1.0
                        opObtainRateTable[card]  = 0.0
                    else:
                        ownObtainRateTable[card] = 0.2677608248519451
                        opObtainRateTable[card]  = 0.7322391751480549
            else:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    ownObtainRateTable[card] = 0.3672518987681677
                    opObtainRateTable[card]  = 0.2994147678984989
        elif m_state == (2, 2, 0, 0, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 1.0
                opObtainRateTable[card]  = 0.0
        elif m_state == (0, 0, 2, 0, 2):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in myObtained:
                    ownObtainRateTable[card] = 1.0
                    opObtainRateTable[card]  = 0.0
                else:
                    ownObtainRateTable[card] = 0.0
                    opObtainRateTable[card]  = 1.0
        elif m_state == (0, 0, 0, 2, 2):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in opObtained:
                    ownObtainRateTable[card] = 0.0
                    opObtainRateTable[card]  = 1.0
                else:
                    ownObtainRateTable[card] = 0.33479308520426937
                    opObtainRateTable[card]  = 0.6652069147957306
        elif m_state == (1, 3, 0, 0, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 1.0
                opObtainRateTable[card]  = 0.0
        elif m_state == (1, 0, 0, 1, 2):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in opObtained:
                    ownObtainRateTable[card] = 0.0
                    opObtainRateTable[card]  = 1.0
                else:
                    ownObtainRateTable[card] = 0.6726046223786418
                    opObtainRateTable[card]  = 0.32739537762135806
        elif m_state == (1, 1, 2, 0, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 1.0
                opObtainRateTable[card]  = 0.0
        elif m_state == (1, 1, 0, 0, 2):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in myHand or card in board:
                    ownObtainRateTable[card] = 1.0
                    opObtainRateTable[card]  = 0.0
                else:
                    ownObtainRateTable[card] = 0.0
                    opObtainRateTable[card]  = 1.0
        elif m_state == (0, 2, 0, 2, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 0.19892253086676845
                opObtainRateTable[card]  = 0.4677441357998982
        elif m_state == (1, 2, 0, 1, 0):
            if hold in [[m,1],[m,2],[m,3],[m,4]]:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    if card in myHand or card == pick:
                        ownObtainRateTable[card] = 1.0
                        opObtainRateTable[card]  = 0.0
                    else:
                        ownObtainRateTable[card] = 0.27208588957055213
                        opObtainRateTable[card]  = 0.7279141104294479
            else:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    if card in myHand:
                        ownObtainRateTable[card] = 1.0
                        opObtainRateTable[card]  = 0.0
                    else:
                        ownObtainRateTable[card] = 0.26882163144739835
                        opObtainRateTable[card]  = 0.7311783685526017
        elif m_state == (0, 0, 4, 0, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 1.0
                opObtainRateTable[card]  = 0.0
        elif m_state == (0, 3, 0, 1, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 0.30808080808080807
                opObtainRateTable[card]  = 0.6919191919191919
        elif m_state == (0, 0, 0, 0, 4):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 0.0
                opObtainRateTable[card]  = 1.0
        elif m_state == (1, 0, 2, 1, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                if card in myObtained:
                    ownObtainRateTable[card] = 1.0
                    opObtainRateTable[card]  = 0.0
                else:
                    ownObtainRateTable[card] = 0.6563044715704256
                    opObtainRateTable[card]  = 0.34369552842957435
        elif m_state == (0, 1, 0, 3, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 0.1874217172531972
                opObtainRateTable[card]  = 0.47924494941346946
        elif m_state == (2, 1, 0, 1, 0):
            if hold in [[m,1],[m,2],[m,3],[m,4]]:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    if card == hold or card in board:
                        ownObtainRateTable[card] = 1.0
                        opObtainRateTable[card]  = 0.0
                    else:
                        ownObtainRateTable[card] = 0.6563044715704256
                        opObtainRateTable[card]  = 0.34369552842957435
            else:
                for card in [[m,1],[m,2],[m,3],[m,4]]:
                    ownObtainRateTable[card] = 0.5608369778099601
                    opObtainRateTable[card]  = 0.4391630221900399
        elif m_state == (4, 0, 0, 0, 0):
            for card in [[m,1],[m,2],[m,3],[m,4]]:
                ownObtainRateTable[card] = 1.0
                opObtainRateTable[card]  = 0.0
    return ownObtainRateTable,opObtainRateTable

def calcYakuProb(myObtainProb, opObtainProb):
    pass

# observationパーサー

class Observation:
    def __init__(self, observation):
        self.observation = observation
        self.hold = None
        self.pick = None
    @property
    def myHand(self):
        return list(set(self.observation['your_hand'] + [self._hold]))
    @property
    def board(self):
        return list(set(self.observation['field'] + [self._pick]))
    @property
    def myObtained(self):
        return list(set(
              self.observation['your_Light']
            + self.observation['your_Seed']
            + self.observation['your_Ribbon']
            + self.observation['your_Dross']
        ))
    @property
    def opObtained(self):
        return self.observation['op_pile']
    @property
    def unknown(self):
        cardset = card_set_factory()
        for c in self.myHand():
            cardset.remove(c)
        for c in self.board():
            cardset.remove(c)
        for c in self.myObtained():
            cardset.remove(c)
        for c in self.opObtained():
            cardset.remove(c)
        return cardset

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．

from typing import List

class MyAgent(CustomAgentBase):
    hold: List[List[int]]
    def __init__(self):
        self.hold = None
        super().__init__()
    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        # ランダムに取れる行動をする
        self.hold = observation['turn']
        observation
        return random.choice(observation['legal_action'])


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
