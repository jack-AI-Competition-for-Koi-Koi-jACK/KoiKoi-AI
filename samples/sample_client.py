import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．


class MyAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()
        f = open("log.txt", "w")
        f.close()

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        f = open("log.txt", "a")
        f.write(observation["state"])
        f.write("\n")
        for i in observation["legal_action"]:
            f.write(str(i))
            f.write(" ")
        f.write("\n")
        f.close()
        if len(observation["legal_action"]) == 1:
            return observation["legal_action"][0]
        if observation["state"] == "koikoi":
            if len(observation["op_Light"]) >= 2:
                return observation["legal_action"][1]
            if len(observation["op_Seed"]) >= 3:
                return observation["legal_action"][1]
            if len(observation["op_Ribbon"]) >= 3:
                return observation["legal_action"][1]
            if len(observation["op_Dross"])>= 7:
                return observation["legal_action"][1]
            return observation["legal_action"][0]
        if observation["state"] == "discard-pick" or observation["state"] == "draw-pick":
            return random.choice(observation["legal_action"])
        if observation["state"] == "discard":
            field_num = [0]*13
            hand_num = [0]*13
            picked_num = [0]*13
            for i in observation["field"]:
                field_num[i[0]] += 1
            for i in observation["your_hand"]:
                hand_num[i[0]] += 1
            for i in observation["op_Light"]:
                picked_num[i[0]] += 1
            for i in observation["op_Seed"]:
                picked_num[i[0]] += 1
            for i in observation["op_Ribbon"]:
                picked_num[i[0]] += 1
            for i in observation["op_Dross"]:
                picked_num[i[0]] += 1
            for i in observation["your_Light"]:
                picked_num[i[0]] += 1
            for i in observation["your_Seed"]:
                picked_num[i[0]] += 1
            for i in observation["your_Ribbon"]:
                picked_num[i[0]] += 1
            for i in observation["your_Dross"]:
                picked_num[i[0]] += 1
            score = [0]*(len(observation["legal_action"]))
            for idx, x in enumerate(observation["legal_action"]):
                month = x[0]
                if(picked_num[month]+field_num[month]+hand_num[month] == 4):
                    score[idx] = 3
                elif(field_num[month] == 0):
                    if(picked_num[month] == 2):
                        score[idx] = 5
                    elif(hand_num[month] == 1):
                        score[idx] = 4
                    else:
                        score[idx] = 6
                elif(field_num[month] == 1):
                    if(hand_num[month] == 1):
                        score[idx] = 0
                    else:
                        score[idx] = 1
                else:
                    score[idx] = 2
            f = open("log.txt", "a")
            for i in score:
                f.write(str(i))
                f.write(" ")
            f.write("\n")
            f.close()
            return observation["legal_action"][score.index(min(score))]
        return random.choice(observation["legal_action"])


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
