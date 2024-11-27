import io
import os
import pickle
import random
import sys

import numpy as np
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.agent import CustomAgentBase
from client.client import SocketIOClient

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．


class MyAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        # tensor情報を盤面から読み取る必要がある場合には次のように取得してください。
        # print(observation.keys())  # ['turn', 'state', 'op_total_point', 'op_yaku', 'op_Light', 'op_Seed', 'op_Ribbon', 'op_Dross', 'op_pile', 'field', 'your_hand', 'your_yaku', 'your_Light', 'your_Seed', 'your_Ribbon', 'your_Dross', 'your_total_point', 'koikoi', 'show', 'legal_action', 'feature_tensor']
        buffer = io.BytesIO(observation["feature_tensor"])
        loaded_numpy_array = np.load(buffer)
        feature_tensor = torch.from_numpy(loaded_numpy_array)
        # print(f"a{feature_tensor.shape}")  # torch.Size([300, 48])

        # ランダムに取れる行動をする
        return random.choice(observation.legal_actions())


if __name__ == "__main__":
    my_agent = MyAgent()  # 参加者が実装したプレイヤーをインスタンス化

    # mode = int(
    #     input(
    #         "Enter mode (1 for playing against AI, 2 for playing against another client): "
    #     )
    # )
    mode = 1
    # num_games = int(input("Enter number of games to play: "))
    num_games = 1
    # player_name = input("Enter your player name: ")
    player_name = 1

    sio_client = SocketIOClient(
        ip="localhost",
        port=15000,
        namespace="/koi-koi",
        agent=my_agent,
        room_id=123,
        player_name=player_name,
        mode=mode,
        num_games=num_games,
    )
    sio_client.run()
    # sio.client.enter_room()
