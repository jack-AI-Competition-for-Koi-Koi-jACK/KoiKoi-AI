import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from client.client import SocketIOClient
from client.agent import CustomAgentBase
from koikoigame.koikoiagent import Arena
from samples.enpitu import EnpituAgent
from samples.hamao_mero import HamaoMeroAgent
from samples.mono import MonoAgent
from samples.sattun_mina import SattunMinaAgent
from samples.yaduya_burnum import YaduyaBurnumAgent
from custom_client_takakura_kazushi import KateTakakuraAgent




class MyAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        # ランダムに取れる行動をする
        return random.choice(observation["legal_action"])


if __name__ == "__main__":
    my_agent = KateTakakuraAgent()  # 参加者が実装したプレイヤーをインスタンス化
    op_agent = MyAgent()  # 対戦したいプレイヤーをインスタンス化
    arena = Arena(my_agent, op_agent)
    arena.multi_game_test(2000)
    print(arena.test_result_str())
