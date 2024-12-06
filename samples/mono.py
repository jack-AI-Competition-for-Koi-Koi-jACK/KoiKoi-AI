import sys
import os
import copy
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．


class MonoAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()
        self.card_importance_ = [[0,0,0,0,0],[0,40,30,10,10],[0,10,30,10,10],[0,200,30,10,10],[0,10,20,10,10],[0,10,20,10,10],[0,20,30,10,10],[0,20,20,10,10],[0,200,10,10,10],[0,1000,30,10,10],[0,20,30,10,10],[0,25,10,20,10],[0,40,10,10,10]]
        self.importance_sum_ = [0,90,60,250,50,50,70,60,230,1050,70,65,70]
        self.light = [1,3,8,11,12]
        self.inoshika = [6,7,10]
        self.aka = [1,2,3]
        self.ao = [6,9,10]

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        if len(observation["legal_action"]) == 1:
            return observation["legal_action"][0]
        if observation["state"] == "koikoi":
            if len(observation["op_Light"]) >= 2 and len(observation["your_Light"]) <= 2:
                return observation["legal_action"][1]
            if len(observation["op_Seed"]) >= 3:
                return observation["legal_action"][1]
            if len(observation["op_Ribbon"]) >= 3:
                return observation["legal_action"][1]
            if len(observation["op_Dross"])>= 6:
                return observation["legal_action"][1]
            return observation["legal_action"][0]
        if observation["state"] == "discard-pick" or observation["state"] == "draw-pick":
            score = [0]*(len(observation["legal_action"]))
            for idx, x in enumerate(observation["legal_action"]):
                score[idx] = self.card_importance_[x[0]][x[1]]
            return observation["legal_action"][score.index(max(score))]
        if observation["state"] == "discard":
            card_importance = copy.deepcopy(self.card_importance_)
            importance_sum = self.importance_sum_.copy()
            field_num = [0]*13
            hand_num = [0]*13
            picked_num = [0]*13
            minus_point = [0]*13
            card_num = [4]*13
            your_light = 0
            op_light = 0
            your_inoshika = 0
            op_inoshika = 0
            your_aka = 0
            op_aka = 0
            your_ao = 0
            op_ao = 0
            for i in observation["your_Light"]:
                if i[0] != 11:
                    your_light += 1
            for i in observation["op_Light"]:
                if i[0] != 11:
                    op_light += 1
            for i in observation["your_Seed"]:
                if i[0] in self.inoshika:
                    your_inoshika += 1
            for i in observation["op_Seed"]:
                if i[0] in self.inoshika:
                    op_inoshika += 1
            for i in observation["your_Ribbon"]:
                if i[0] in self.aka:
                    your_aka += 1
                elif i[0] in self.ao:
                    your_ao += 1
            for i in observation["op_Ribbon"]:
                if i[0] in self.aka:
                    op_aka += 1
                elif i[0] in self.ao:
                    op_ao += 1
            if your_light >= 2 and op_light >= 2:
                for x in self.light:
                    importance_sum[x] -= card_importance[x][1]
                    card_importance[x][1] = 0
            if your_inoshika >= 1 and op_inoshika >= 1:
                for x in self.inoshika:
                    importance_sum[x] -= 20
                    card_importance[x][1] = 10
            if your_aka >= 1 and op_aka >= 1:
                for x in self.aka:
                    importance_sum[x] -= 10
                    card_importance[x][2] = 20
            if your_ao >= 1 and op_ao >= 1:
                for x in self.ao:
                    importance_sum[x] -= 10
                    card_importance[x][2] = 20

            for i in observation["field"]:
                field_num[i[0]] += 1
            for i in observation["your_hand"]:
                hand_num[i[0]] += 1
            for i in observation["op_Light"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            for i in observation["op_Seed"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            for i in observation["op_Ribbon"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            for i in observation["op_Dross"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            for i in observation["your_Light"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            for i in observation["your_Seed"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            for i in observation["your_Ribbon"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            for i in observation["your_Dross"]:
                minus_point[i[0]] += card_importance[i[0]][i[1]]
                picked_num[i[0]] += 1
                card_num[i[0]] -= 1
            score = [0]*(len(observation["legal_action"]))
            for idx, x in enumerate(observation["legal_action"]):
                month = x[0]
                if(picked_num[month]+field_num[month]+hand_num[month] == 4):
                    score[idx] = (importance_sum[month] - minus_point[month])/(card_num[month]) + card_importance[month][x[1]]/4
                elif(field_num[month] == 0):
                    if(picked_num[month] == 2):
                        score[idx] = -(card_importance[month][x[1]])*1
                    elif(hand_num[month] == 1):
                        score[idx] = -(card_importance[month][x[1]])*1.4
                    else:
                        score[idx] = -(card_importance[month][x[1]])*0.6
                elif(field_num[month] == 1):
                    if(hand_num[month] == 1):
                        score[idx] = 100 + (importance_sum[month] - minus_point[month])/(card_num[month]) + card_importance[month][x[1]]/4 + 2
                    else:
                        score[idx] = 100 + (importance_sum[month] - minus_point[month])/(card_num[month]) + card_importance[month][x[1]]/4 + 1
                else:
                    score[idx] = 100 + (importance_sum[month] - minus_point[month])/(card_num[month]) + card_importance[month][x[1]]/4
            return observation["legal_action"][score.index(max(score))]
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