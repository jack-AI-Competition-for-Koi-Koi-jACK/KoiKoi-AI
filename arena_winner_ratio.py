import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

df = pd.read_csv('winner.csv')

menber_list =[
        "Mono",
        # "Hamao Mero",
        "Enpitu",
        "SattunMina",
        "YaduyaBurnum",
        "KateTakakura",
        "randomagent"
]

ja_menber_list =[
        "mono AI",
        # "ハマオメロ",
        "えんぴつ AI ",
        "さっつん みな AI ",
        "やづや バーナム BI ",
        "kate 鉄壁 AI ",
        "ランダム AI"
]
for i in range(len(menber_list)):
    for j in range(i+1,len(menber_list)):
        column_name = f'{menber_list[i]}vs{menber_list[j]}'
        battle_data = df[column_name]
        # numpy変換
        battle_data = battle_data.to_numpy()
        # 勝率を逐次計算してそれをプロットする
        win_rate = np.cumsum(battle_data == 1) / (np.arange(len(battle_data)) + 1)
        if win_rate[-1] < 0.5:
            winner = ja_menber_list[j]
        else:
            winner = ja_menber_list[i]
        fig,ax = plt.subplots()
        ax.plot(win_rate)
        ax.set_xlabel('number of games')
        ax.set_ylabel('win rate')
        ax.set_xlim(0, len(battle_data))
        ax.set_ylim(0, 1)
        ax.text(600, 0.5, winner, fontsize=15,color='red')
        ax.text(600, 0.2, win_rate[-1], fontsize=15,color='red')
        ax.set_title(f'{ja_menber_list[i]} vs {ja_menber_list[j]}' + 'win rate')
        plt.savefig(f'figure/{column_name}.png')
        