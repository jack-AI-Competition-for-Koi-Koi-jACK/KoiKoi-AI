import sys
import os
import random
import pandas as pd
import numpy as np

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
# 総当たり戦
def round_robin(battle_list, observation):
    result = []
    for i in range(0,len(battle_list)):
        for j in range(i+1,len(battle_list)):
            arena = Arena(battle_list[i], battle_list[j])
            arena.multi_game_test(1)
            result.append(arena.test_result_str())
            print(arena.test_result_str())
    return result


if __name__ == "__main__":
    Mono = MonoAgent()
    Enpitu = EnpituAgent()
    Hamao_Mero = HamaoMeroAgent()
    Sattun_Mina = SattunMinaAgent()
    Yaduya_Burnum = YaduyaBurnumAgent()
    Kate_Takakura = KateTakakuraAgent()
    # ランダムAIとの対戦も入れる
    random_agent = MyAgent()
    
    battle_list = [
        Mono,
        Enpitu,
        Hamao_Mero,
        Sattun_Mina,
        Yaduya_Burnum,
        Kate_Takakura,
        random_agent,
        
    ]
    
    menber_list =[
        "Mono",
        "Hamao Mero",
        "Enpitu",
        "SattunMina",
        "YaduyaBurnum",
        "KateTakakura",
        "randomagent"
    ]
    winner_df = pd.DataFrame([])
    
    for i in range(0,len(battle_list)):
        for j in range(i+1,len(battle_list)):
            battle_result = ['draw', menber_list[i], menber_list[j]]
            arena = Arena(battle_list[i], battle_list[j])
            arena.multi_game_test(100)
            print(arena.test_winner)
            print(menber_list[i],'vs',menber_list[j], arena.test_result_str())
            print(battle_result[arena.winner])
            
            df = pd.DataFrame(arena.test_winner, columns=[f'{menber_list[i]}vs{menber_list[j]}'])
            winner_df = pd.concat([winner_df, df], axis=1)
    
    winner_df.to_csv('winner_100.csv')   
        