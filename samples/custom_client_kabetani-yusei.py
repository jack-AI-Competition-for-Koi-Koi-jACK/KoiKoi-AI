import sys
import os
import random
import pickle
import torch
import io
import numpy as np 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase

from kabetani_yusei_api.main import KabetaniYuseiAPI
MyAPI = KabetaniYuseiAPI()

class MyAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()

    def custom_act(self, observation):
        # 邪魔な特徴量を削除する
        if 'feature_tensor' in observation:
            del observation['feature_tensor']

        # 行動を決定する
        try:
            action = MyAPI.action(observation)
            return action
        except Exception as e:
            print(f"Error is {e}")
            return random.choice(observation.legal_actions())

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
