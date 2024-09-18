import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase

from samples.Observation import Observation
from samples.CardProbTable import CardProbTable
from samples.Card import Card, Pair
from samples.RoleProbTable import RoleProbTable, contains_tane, contains_kasu, contains_tann

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
