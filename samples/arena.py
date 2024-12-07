import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from client.client import SocketIOClient
from client.agent import CustomAgentBase
from koikoigame.koikoiagent import Arena
from enpitu import EnpituAgent
from hamao_mero import HamaoMeroAgent
from mono import MonoAgent
from sattun_mina import SattunMinaAgent
from yaduya_burnum import YaduyaBurnumAgent




class MyAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        # ランダムに取れる行動をする
        
        return random.choice(observation["legal_action"])
    
    def act(self, observation):
        try:
            return self.custom_act(observation)
        except:
            legal_actions = observation["legal_action"]
            if len(legal_actions) == 1:
                return legal_actions[0]
            for action in legal_actions:
                if action is None or action is False:
                    return action
            return legal_actions[0]  # デフォルトアクション


if __name__ == "__main__":
    my_agent = SattunMinaAgent()  # 参加者が実装したプレイヤーをインスタンス化
    op_agent = YaduyaBurnumAgent()  # 対戦したいプレイヤーをインスタンス化
    arena = Arena(my_agent, op_agent)
    arena.multi_game_test(100)
    print(arena.test_result_str())

