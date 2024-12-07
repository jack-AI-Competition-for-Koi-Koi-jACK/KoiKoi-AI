import io
import os
import pickle
import random
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from base_models.koikoinet2L import DiscardModel, KoiKoiModel, PickModel
from client.agent import CustomAgentBase
from client.client import SocketIOClient

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．


class DrawModel(torch.nn.Module):
    def forward(self, x):
        return torch.zeros((1, 1))


class KateTakakuraAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()
        checkpoint_dir = Path(os.path.abspath(__file__)).parent / "checkpoints"
        discard_model = torch.load(
            checkpoint_dir / "discard.pt", map_location=torch.device("cpu")
        )
        pick_model = torch.load(
            checkpoint_dir / "pick.pt", map_location=torch.device("cpu")
        )
        koikoi_model = torch.load(
            checkpoint_dir / "koikoi.pt", map_location=torch.device("cpu")
        )

        self.model = {
            "discard": discard_model,
            "discard-pick": pick_model,
            "draw-pick": pick_model,
            "koikoi": koikoi_model,
            "draw": DrawModel(),
        }

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        # tensor情報を盤面から読み取る必要がある場合には次のように取得してください。
        # print(observation.keys())  # ['turn', 'state', 'op_total_point', 'op_yaku', 'op_Light', 'op_Seed', 'op_Ribbon', 'op_Dross', 'op_pile', 'field', 'your_hand', 'your_yaku', 'your_Light', 'your_Seed', 'your_Ribbon', 'your_Dross', 'your_total_point', 'koikoi', 'show', 'legal_action', 'feature_tensor']
        legal_action = observation["legal_action"]

        # 取れる選択肢が1つの時はそれを返却
        if len(legal_action) == 1:
            return legal_action[0]

        buffer = io.BytesIO(observation["feature_tensor"])
        loaded_numpy_array = np.load(buffer)
        feature_tensor = torch.from_numpy(loaded_numpy_array)
        feature_tensor = feature_tensor.reshape(
            1, feature_tensor.shape[0], feature_tensor.shape[1]
        )
        if observation["state"] not in self.model.keys():
            print("** FATAL: unknown state. model not found")
            print(observation["state"])
            print(legal_action)

        output = self.model[observation["state"]](feature_tensor).squeeze(0).detach()

        action = self.output_to_legal_action(output, legal_action)
        print("===")
        print(output)
        print(output.argmax())
        print(observation["state"])
        print(observation["legal_action"])
        print(action)

        # print(f"a{feature_tensor.shape}")  # torch.Size([300, 48])
        # ランダムに取れる行動をする
        return random.choice(observation["legal_action"])

    def output_to_legal_action(self, output, legal_action):
        if type(legal_action[0]) is bool:
            # stateがkoikoiのとき
            return legal_action[torch.argmax(output)]
        else:
            sorted_indices = torch.argsort(output, descending=True)
            for i in sorted_indices:
                action = [(i // 4 + 1).item(), (i % 4 + 1).item()]
                if action in legal_action:
                    return action
            print("** FATAL: action not found")
        return legal_action[0]


if __name__ == "__main__":
    my_agent = MyAgent()  # 参加者が実装したプレイヤーをインスタンス化

    mode = int(
        input(
            "Enter mode (1 for playing against AI, 2 for playing against another client): "
        )
    )
    # mode = 1
    num_games = int(input("Enter number of games to play: "))
    # num_games = 1
    player_name = input("Enter your player name: ")
    # player_name = 1

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