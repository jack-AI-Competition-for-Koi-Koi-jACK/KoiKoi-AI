import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.client import SocketIOClient
from client.agent import CustomAgentBase

# 各カードについて取得できる確率をヒューリスティックで求める．
def make_obtain_prob_table(observation):
    m_remains = {
        m: 4
        for m in range(1,12+1)
    }
    
    m_exists_on_hand = {
        m: 0
        for m in range(1,12+1)
    }
    
    for c in observation['your_hand']:
        m_exists_on_hand[c[0]] += 1

    m_exists_on_field = {
        m: 0
        for m in range(1,12+1)
    }

    for c in observation['field']:
        m_exists_on_field[c[0]] += 1

    num_of_unknown = 4*12
    
    num_of_opp_hand = 8 - (observation['turn']//2)

    # 今後自分がその札を引ける確率
    own_obtain_prob_table = {
        [m,i]: None
        for i in range(1,4+1) 
        for m in range(1,12+1)
    }

    # 自分がその札を捨てた/残したときに相手がその札を取れる確率
    opp_obtain_prob_table = {
        [m,i]: None
        for i in range(1,4+1) 
        for m in range(1,12+1)
    }
    
    cards_in_own_obtained \
    = list(set( observation['your_Dross']
    + observation['your_Ribbon']
    + observation['your_Seed']
    + observation['your_Light']))
    
    for c in cards_in_own_obtained:
        own_obtain_prob_table[c] = 1
        opp_obtain_prob_table[c] = 0
        m_remains[c[0]] -= 1
        num_of_unknown -= 1
    
    cards_in_opp_obtained = observation['op_pile']

    for c in cards_in_opp_obtained:
        own_obtain_prob_table[c] = 0
        opp_obtain_prob_table[c] = 1
        m_remains[c[0]] -= 1
        num_of_unknown -= 1
    
    for c in own_obtain_prob_table:
        if   m_remains[c[0]] == 0: continue
        elif m_remains[c[0]] == 2: 
            if m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 2:
                # unknown 0
                own_obtain_prob_table[c] = 1 
                opp_obtain_prob_table[c] = 0
            elif m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 1:
                # unknown 1 
                # 残り一枚が山札にある確率 ( 山札 / 山札+相手の手札 )
                # * 山札を相手，自分に半分に振り分けるとして，自身の方に入る確率 ( 1/2 )
                pile = num_of_unknown - num_of_opp_hand
                in_pile = pile / num_of_unknown
                own_obtain_prob_table[c] = in_pile/2
                # 残り一枚が山札にある確率 ( 山札 / 山札+相手の手札 )
                # * 山札を相手，自分に半分に振り分けるとして，相手の方に入る確率 ( 1/2 )
                # + 残り一枚が相手手札にある確率 ( 1 - 山札/(山札+相手の手札) )
                opp_obtain_prob_table[c] = 1 - in_pile/2
            elif m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 0:
                # unknown 2
                # 二枚とも山札にある確率 ( 山札C2 / (山札+相手の手札)C2 )
                # * 山札を相手，自分に半分に振り分けるとして，自身の方に入る確率 ( (山札/2)C2 / 山札C2 )
                # 山札C2がキャンセルされる．またCombinationの分母もキャンセルされることに注意する．
                unknownC2 = num_of_unknown*(num_of_unknown-1)#/2
                pile = num_of_unknown - num_of_opp_hand
                half_pile = pile//2
                half_pileC2 = half_pile*(half_pile - 1)#/2
                own_obtain_prob_table[c] = half_pileC2/unknownC2
                # 二枚とも山札にある確率 ( 山札C2 / (山札+相手の手札)C2 )
                # * 山札を相手，自分に半分に振り分けるとして，自身の方に入る確率 ( (山札/2)C2 / 山札C2 )
                # + 相手が一枚以上持っている確率 ( 1 - 山札C2/(山札+相手の手札)C2 )
                pileC2 = pile*(pile - 1)#/2
                opp_obtain_prob_table[c] = half_pileC2/unknownC2 + 1 - pileC2/unknownC2
        elif m_remains[c[0]] == 4: 
            if m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 4:
                # unknown 0
                own_obtain_prob_table[c] = 1
                opp_obtain_prob_table[c] = 0
            elif m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 3:
                # unknown 1
                if m_exists_on_hand[c[0]] > 0:
                    # 残り一枚が山札にある確率 ( 山札 / 山札+相手の手札 )
                    # * 山札を相手，自分に半分に振り分けるとして，自身の方に入る確率 ( 1/2 )
                    # /2
                    # + 1/2
                    in_pile = (num_of_unknown - num_of_opp_hand) / num_of_unknown
                    own_obtain_prob_table[c] = in_pile/4 + 1/2
                    # 残り一枚が山札にある確率 ( 山札 / 山札+相手の手札 )
                    # * 山札を相手，自分に半分に振り分けるとして，相手の方に入る確率 ( 1/2 )
                    # + 残り一枚が相手の手札にある確率 ( 1 - 山札 / 山札+相手の手札 )
                    opp_obtain_prob_table[c] = 1 - in_pile/2
                else: 
                    # 残り一枚が山札にある確率 ( 山札 / 山札+相手の手札 )
                    # * 山札を相手，自分に半分に振り分けるとして，自身の方に入る確率 ( 1/2 )
                    in_pile = (num_of_unknown - num_of_opp_hand) / num_of_unknown
                    own_obtain_prob_table[c] = in_pile/2
                    # 残り一枚が山札にある確率 ( 山札 / 山札+相手の手札 )
                    # * 山札を相手，自分に半分に振り分けるとして，相手の方に入る確率 ( 1/2 )
                    # + 残り一枚が相手の手札にある確率 ( 1 - 山札 / 山札+相手の手札 )
                    opp_obtain_prob_table[c] = 1 - in_pile/2
            elif m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 2:
                if   m_exists_on_hand[c[0]] == 2: pass
                    #相手が一枚以上持っている確率
                elif m_exists_on_hand[c[0]] == 1: pass
                    #相手が一枚以上持っている確率
                elif m_exists_on_hand[c[0]] == 0: pass
                    #相手が一枚以上持っている確率
            elif m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 1:
                if m_exists_on_hand[c[0]] == 1: pass
                elif m_exists_on_hand[c[0]] == 0: pass
            elif m_exists_on_hand[c[0]] + m_exists_on_field[c[0]] == 0: pass
                # unknown 4

# CustomAgentBase を継承して，
# custom_act()を編集してコイコイAIを実装してください．

class MyAgent(CustomAgentBase):
    def __init__(self):
        super().__init__()

    def custom_act(self, observation):
        """盤面情報と取れる行動を受け取って，行動を決定して返す関数．参加者が各自で実装．"""
        # ランダムに取れる行動をする
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
    # sio.client.enter_room()
