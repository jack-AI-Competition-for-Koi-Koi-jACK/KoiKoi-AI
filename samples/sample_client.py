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
        self.crane = {(1, 1)}
        self.curtain = {(3, 1)}
        self.moon = {(8, 1)}
        self.rainman = {(11, 1)}
        self.phoenix = {(12, 1)}
        self.sake = {(9, 1)}
        
        self.light = {(1, 1), (3, 1), (8, 1), (11, 1), (12, 1)}
        self.seed = {(2, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 2), (9, 1), (10, 1), (11, 2)}
        self.ribbon = {
        (1, 2),(2, 2),(3, 2),(4, 2),(5, 2),
        (6, 2),(7, 2),(9, 2),(10, 2),(11, 3),
        }
        self.dross = {
        (1, 3),(1, 4),(2, 3),(2, 4),(3, 3),(3, 4),(4, 3),(4, 4),(5, 3),(5, 4),(6, 3),(6, 4),
        (7, 3),(7, 4),(8, 3),(8, 4),(9, 3),(9, 4),(10, 3),(10, 4),(11, 4),(12, 2),(12, 3),(12, 4),
        }
        
        self.boar_deer_butterfly = {(6, 1), (7, 1), (10, 1)}
        self.flower_sake = {(3, 1), (9, 1)}
        self.moon_sake = {(8, 1), (9, 1)}
        self.red_ribbon = {(1, 2), (2, 2), (3, 2)}
        self.blue_ribbon = {(6, 2), (9, 2), (10, 2)}
        self.red_blue_ribbon = {(1, 2), (2, 2), (3, 2), (6, 2), (9, 2), (10, 2)}

        # 青タン重視
        self.barnum_choice= [[9,1],[3,1],[8,1],[1,1],[12,1],[9,2],[11,1],[6,2],[10,2],[6,1],[10,1],[3,2],[7,1],[1,2],[2,2],[7,2],[8,2],[11,2],[2,1],[4,1],[5,1],[11,3],[4,2],[5,2],[9,3],[9,4],[3,3],[3,4],[8,3],[8,4],[1,3],[1,4],[11,4],[6,3],[6,4],[10,3],[10,4],[7,3],[7,4],[12,2],[12,3],[12,4],[2,3],[2,4],[4,3],[4,4],[5,3],[5,4]]
        # 赤タン重視
        self.barnum_choice_2= [[9,1],[3,1],[8,1],[1,1],[12,1],[11,1],[3,2],[9,2],[1,2],[2,2],[6,2],[10,2],[2,1],[6,1],[10,1],[7,1],[7,2],[8,2],[11,2],[4,1],[5,1],[11,3],[4,2],[5,2],[9,3],[9,4],[3,3],[3,4],[8,3],[8,4],[1,3],[1,4],[11,4],[6,3],[6,4],[10,3],[10,4],[7,3],[7,4],[12,2],[12,3],[12,4],[2,3],[2,4],[4,3],[4,4],[5,3],[5,4]]
        # 猪鹿蝶重視
        self.barnum_choice_3= [[9,1],[3,1],[8,1],[1,1],[12,1],[9,2],[11,1],[6,1],[10,1],[7,1],[6,2],[10,2],[7,2],[3,2],[1,2],[2,2],[8,2],[11,2],[2,1],[4,1],[5,1],[11,3],[4,2],[5,2],[6,3],[6,4],[10,3],[10,4],[7,3],[7,4],[9,3],[9,4],[3,3],[3,4],[8,3],[8,4],[1,3],[1,4],[11,4],[12,2],[12,3],[12,4],[2,3],[2,4],[4,3],[4,4],[5,3],[5,4]]
        # タネ重視
        self.barnum_choice_4= [[9,1],[3,1],[8,1],[1,1],[12,1],[9,2],[11,1],[6,1],[10,1],[7,1],[6,2],[10,2],[3,2],[2,2],[8,2],[1,2],[7,2],[11,2],[2,1],[4,1],[5,1],[11,3],[4,2],[5,2],[9,3],[9,4],[3,3],[3,4],[8,3],[8,4],[1,3],[1,4],[11,4],[6,3],[6,4],[10,3],[10,4],[7,3],[7,4],[12,2],[12,3],[12,4],[2,3],[2,4],[4,3],[4,4],[5,3],[5,4]]
        # タン重視
        self.barnum_choice_5= [[9,1],[3,1],[8,1],[1,1],[12,1],[9,2],[11,1],[6,2],[10,2],[3,2],[6,1],[10,1],[1,2],[2,2],[7,1],[7,2],[11,3],[4,2],[5,2],[2,1],[4,1],[5,1],[8,2],[11,2],[9,3],[9,4],[3,3],[3,4],[8,3],[8,4],[1,3],[1,4],[11,4],[6,3],[6,4],[10,3],[10,4],[7,3],[7,4],[12,2],[12,3],[12,4],[2,3],[2,4],[4,3],[4,4],[5,3],[5,4]]

    def custom_act(self, observation):
        if observation.state == "discard":
            # 組み合わせられる順に選ぶ
            for hand in self.barnum_choice_2:
                if hand in observation['your_hand']&observation['field']:
                    return hand
            # なければ，逆順で選ぶ
            for hand in self.barnum_choice_2[::-1]:
                if hand in observation['your_hand']:
                    return hand
                
        
        elif observation.state == "discard-pick":
            for hand in self.barnum_choice_2:
                if hand in observation['legal_action']:
                    return hand
        
        elif observation.state == "draw-pick":
            for hand in self.barnum_choice_2:
                if hand in observation['legal_action']:
                    return hand
        elif observation.state == "koikoi":
            #自分の現在の得点が相手より高いとき
            #if round_point[1] > round_point[2]:
                #print("RP1>RP2")
                #return False
            #5ターン以上が経過して役が完成したとき
            if observation.turn >= 5 :
                #print("5turn")
                return False
            #5点以上を獲得できるとき
            elif observation.your_total_point >= 5 :
                #print("5point")
                return False
            #相手がこいこいをしているとき
            elif sum(observation.koikoi[2]) > 0 :
                #print("koikoi")
                return False
            #上記のいずれにも該当しない場合はこいこい
            else :
                return True


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
        port=5001,
        namespace="/koi-koi",
        agent=my_agent,
        room_id=123,
        player_name=player_name,
        mode=mode,
        num_games=num_games,
    )
    sio_client.run()
    # sio.client.enter_room()
