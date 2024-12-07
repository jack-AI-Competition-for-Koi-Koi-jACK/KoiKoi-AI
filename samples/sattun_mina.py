import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．

class SattunMinaAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()

    def find_september_tane(self, hand, field, legal_actions):
        for le in legal_actions:
            if le == [9, 1]:
                for fi in field:
                    if fi == [9, 2] or fi == [9, 3] or fi ==[9, 4]:
                        
                        return [9, 1]
        for fie in field:
            if fie == [9, 1]:
                for lea in legal_actions:
                    if lea == [9, 2] or lea == [9, 3] or lea ==[9, 4]:
                        
                        return lea

        
        return None
    
    def hikari(self, hand, field, legal_actions):
        
        for le in legal_actions:
            if le == [3, 1]:
                for fi in field:
                    if fi == [3, 2] or fi == [3, 3] or fi == [3, 4]:
                        
                        return [3, 1]
        for fie in field:
            if fie == [3, 1]:
                for lea in legal_actions:
                    if lea == [3, 2] or lea == [3, 3] or lea == [3, 4]:
                        
                        return lea
        
        for le in legal_actions:
            if le == [8, 1]:
                for fi in field:
                    if fi == [8, 2] or fi == [8, 3] or fi == [8, 4]:
                        
                        return [8, 1]
        for fie in field:
            if fie == [8, 1]:
                for lea in legal_actions:
                    if lea == [8, 2] or lea == [8, 3] or lea ==[8, 4]:
                        
                        return lea
        
        for le in legal_actions:
            if le == [1, 1]:
                for fi in field:
                    if fi == [1, 2] or fi == [1, 3] or fi == [1, 4]:
                        
                        return [1, 1]
        for fie in field:
            if fie == [1, 1]:
                for lea in legal_actions:
                    if lea == [1, 2] or lea ==[1, 3] or lea ==[1, 4]:
                        
                        return lea
        
        for le in legal_actions:
            if le == [12, 1]:
                for fi in field:
                    if fi == [12, 2] or fi == [12, 3] or fi == [12, 4]:
                        
                        return [12, 1]
        for fie in field:
            if fie == [12, 1]:
                for lea in legal_actions:
                    if lea == [12, 2] or lea ==[12, 3] or lea ==[12, 4]:
                        
                        return lea
                    
        for le in legal_actions:
            if le == [11, 1]:
                for fi in field:
                    if fi == [11, 2] or fi == [11, 3] or fi == [11, 4]:
                        
                        return [11, 1]
        for fie in field:
            if fie == [11, 1]:
                for lea in legal_actions:
                    if lea == [11, 2] or lea ==[11, 3] or lea ==[11, 4]:
                        
                        return lea
        
        return None
    
    def inosikatyo_husegu(self, hand, field, legal_actions, your_Seed):
        for yo in your_Seed:
            if yo != [6, 1] and yo != [7, 1] and yo != [10, 1]:
                for ha in hand:
                    if ha != [6, 1] and ha != [7, 1] and ha != [10, 1]:
                        for fi in field:
                           if fi == [7, 1]:
                                for le in legal_actions:
                                    if le ==[7, 2] or le == [7, 3] or le == [7, 4]:
                                     
                                     return le
                           elif fi == [6, 1]:
                                for le in legal_actions:
                                   if le ==[6, 2] or le == [6, 3] or le == [6, 4]:
                                    
                                    return le
                           elif fi == [10, 1]:
                                for le in legal_actions:
                                   if le ==[10, 2] or le == [10, 3] or le == [10, 4]:
                                    
                                    return le
        return None
    
    def aotan_husegu(self, hand, field, legal_actions, your_Ribbon):
        for yo in your_Ribbon:
             if yo != [6, 2] and yo != [9, 2] and yo != [10, 2]:
                 for ha in hand:
                    if ha != [6, 2] and ha != [9, 2] and ha != [10, 2]:
                        for fi in field:
                            if fi == [6, 2]:
                                for le in legal_actions:
                                    if le == [6, 1] or le == [6, 3] or le == [6, 4]:
                                        
                                        return le
                            elif fi == [10, 2]:
                                for le in legal_actions:
                                    if le == [10, 1] or le == [10, 3] or le == [10, 4]:
                                        
                                        return le
                            elif fi == [9, 2]:
                                for le in legal_actions:
                                    if le == [9, 1] or le == [9, 3] or le == [9, 4]:
                                        
                                        return le
        return None

    def akatan_husegu(self, hand, field, legal_actions, your_Ribbon):
        for yo in your_Ribbon:
            if yo != [1, 2] and yo != [2, 2] and yo != [3, 2]:
                for ha in hand:
                    if ha != [1, 2] and ha != [2, 2] and ha != [3, 2]:
                        for fi in field:
                            if fi == [2, 2]:
                                for le in legal_actions:
                                    if le == [2, 1] or le == [2, 3] or le == [2, 4]:
                                        
                                        return le
                            elif fi == [1, 2]:
                                for le in legal_actions:
                                    if le == [1, 1] or le == [1, 3] or le == [1, 4]:
                                        
                                        return le
                            elif fi == [3, 2]:
                                for le in legal_actions:
                                    if le == [3, 1] or le == [3, 3] or le == [3, 4]:
                                        
                                        return le
        return None
                           
            
    def decide_tan_or_tane(self, your_Ribbon, your_Seed,legal_actions):
        my_Ribbon = []
        my_Seed = []
        my_Ribbon += your_Ribbon
        my_Seed += your_Seed
        for legal_action in legal_actions:
            if legal_action[1] == 2:
                my_Ribbon.append(legal_action)
            elif legal_action[1] == 1:
                my_Seed.append(legal_action)
        if len(my_Ribbon) >= len(my_Seed):
            blue = []
            red = []
            for legal_action in legal_actions:
                if legal_action[1] == 2:
                    if legal_action[0] == 6 or legal_action[0] == 10 or legal_action[0] == 12:
                        blue.append(legal_action)
                    else:
                        red.append(legal_action)
            if len(blue) > len(red):
                
                return blue[0]
            else:
                
                return red[0]
        else:
           for legal_action in legal_actions:
                if legal_action[1] == 1:
                     
                     return legal_action
        
        return None
        
    def sort_by_kasu_value(self,data, value_order_1, value_order_2):
        value_dict_1 = {value: index for index, value in enumerate(value_order_1)}
        value_dict_2 = {value: index for index, value in enumerate(value_order_2)}

        def sort_key(item):
            primary_sort = value_dict_2.get(item[1], len(value_order_2)) if 1 <= item[1] <= 4 else len(value_order_2)
            secondary_sort = value_dict_1.get(item[0], len(value_order_1))
            return (primary_sort, secondary_sort)
        
        return sorted(data, key=sort_key)
            
    def only_kasu(self, legal_actions):
        value_order_1 = [4, 5, 11, 2, 6, 7, 10, 12, 1, 3, 8, 9]
        value_order_2 = [1,2,3,4]
        sorted_cards = self.sort_by_kasu_value(legal_actions, value_order_1, value_order_2)
        
        if sorted_cards == []:
            return None
        else:
            
            return sorted_cards[0]


    def dispose_kasu(self,hands,fields, legal_actions):
        same_month = []
        for hand in hands:
            for field in fields:
                if hand[0] == field[0]:
                    same_month.append(field)
        
        value_order_1 = [4, 5, 11, 2, 6, 7, 10, 12, 1, 3, 8, 9]
        value_order_2 = [4, 3, 2, 1]
        sorted_cards = self.sort_by_kasu_value(legal_actions, value_order_1, value_order_2)
        
        if same_month == []:
            
            return None
        else:
            
            return sorted_cards[0] 
    
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

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        hand = observation['your_hand']
        field = observation['field']
        your_yaku = observation['your_yaku']
        your_score = observation['your_total_point']
        your_Seed = observation['your_Seed']
        your_Ribbon = observation["your_Ribbon"]
        op_score = observation['op_total_point']
        game_state = observation['state']
        legal_actions = observation['legal_action']

        if game_state == 'discard':
            #9のタネ取れるなら取る
            if self.find_september_tane(hand, field, legal_actions) != None:
                return self.find_september_tane(hand, field, legal_actions)
            
            #光ふだ 3,8>1>12>11 場札にあるとき優先的に取る
            elif self.hikari(hand, field, legal_actions) != None:
                return self.hikari()
            
            elif self.inosikatyo_husegu(hand, field, legal_actions, your_Seed) != None:
                return self.inosikatyo_husegu(hand, field, legal_actions, your_Seed)
            
            elif self.aotan_husegu(hand, field, legal_actions, your_Ribbon) != None:
                return self.aotan_husegu(hand, field, legal_actions, your_Ribbon)
            
            elif self.akatan_husegu(hand, field, legal_actions, your_Ribbon) != None:
                return self.akatan_husegu(hand, field, legal_actions, your_Ribbon)

            #たんとたねの数を比べて多い方を取る
            elif self.decide_tan_or_tane(your_Ribbon, your_Seed,legal_actions) != None:
                return self.decide_tan_or_tane(your_Ribbon, your_Seed,legal_actions)
            
            #カスだけ取れるなら取る
            elif self.only_kasu(legal_actions) != None:
                return self.only_kasu(legal_actions)
            
            # 何も取れない時 4 5 >11>2>6,7,10>12>1>3,8>9 の順でカス捨てる
            elif self.dispose_kasu(hand,field,legal_actions) != None:
                return  self.dispose_kasu(hand,field,legal_actions)
            
            else:
                return random.choice(observation['legal_action'])
        
        elif game_state == 'koikoi':
            if legal_actions[0] is not None:
                return self.should_koikoi(your_yaku, your_score, op_score)
            else:
                return legal_actions[0]

        else:
            return random.choice(observation['legal_action'])


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