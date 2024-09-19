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
    
    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        
        def find_matching_card(self, hand_cards, fields):
            """手札のカードと一致する場札を探す"""
            print('find_card関数が呼び出されました')
            same_month = []
            for hand_card in hand_cards:
                for field_card in fields:
                    if hand_card[0] == field_card[0]:
                        same_month.append(field_card)
            print('一致する場札:', same_month)
            
            if len(same_month) == 1:
                print('一致する場札が1枚見つかりました:', same_month[0])
                return same_month[0]
            
            elif len(same_month) == 0:
                # 一致する場札がない場合、ランダムで選ぶ
                chosen_card = random.choice(hand_cards)
                print('一致する場札がないため、ランダムで選ばれたカード:', chosen_card)
                return chosen_card
            else:
                # 一致する場札が複数ある場合、点数の高いカードを選ぶ
                same_month.sort(key=lambda x: x[1])
                print('一致する場札が複数あるため、点数の高いカードを選びました:', same_month[0])
                return same_month[0]
        
        def should_koikoi(self, your_yaku, your_score, op_score):
            """こいこいするかどうかを判断する"""
            if your_yaku == []:
                return False  # 役がない場合はこいこいしない
            
            total_yaku_points = sum(yaku[1] for yaku in your_yaku)
            
            # スコアが近い場合、より積極的にこいこいする
            if abs(your_score - op_score) <= 3:
                return True
            
            # スコアが離れている場合、より慎重にこいこいする
            return False
        
        # 手札の情報を取得
        hand = observation['your_hand']
        # 場の情報を取得
        field = observation['field']
        # 自分の役情報を取得
        your_yaku = observation['your_yaku']
        # スコア情報を取得
        your_score = observation['your_total_point']
        op_score = observation['op_total_point']
        # ゲームの状態を取得
        game_state = observation['state']
        # こいこいの状況
        koikoi_situation = observation['koikoi']
        # 取れる行動を取得
        legal_actions = observation['legal_action']
        
        print('--------data----------')
        print('hand', hand)
        print('field', field)
        print('your_yaku', your_yaku)
        print('your_score', your_score)
        print('op_score', op_score)
        print('game_state', game_state)
        print('koikoi_situation', koikoi_situation)
        print('legal_actions', legal_actions)
        print('--STATUS--')
        if game_state == 'discard':
            return find.matching_card(self,hand, field)
        elif game_state == 'koikoi':
            if legal_actions[0] is not None:
                return should_koikoi(self,your_yaku, your_score, op_score)
            else:
                return legal_actions[0]
        else:
            return random.choice(observation['legal_action'])

        print('----------------------')


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