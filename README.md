# Koi-Koi AI

>S. Guan, J. Wang, R. Zhu, J. Qian and Z. Wei, **“Learning to Play Koi-Koi Hanafuda Card Games with Transformers,”** *IEEE Transactions on Artificial Intelligence*, vol. 4, no. 6, pp. 1449-1460, 2023. [doi: 10.1109/TAI.2023.3240674](https://ieeexplore.ieee.org/document/10032777). [\[PDF\]](https://github.com/guansanghai/KoiKoi-AI/raw/main/TAI.2023.3240674.pdf)

Learning based AI for playing multi-round Koi-Koi hanafuda card games. ([@guansanghai](https://github.com/guansanghai))

![Play Interface](/markdown/Kapture.gif)

## Environment

* Python 3
* PyTorch 1.8.1
* PySimpleGUI (for the interface playing vs AI)

## About Koi-Koi Hanafuda Card Games

[Hanafuda](https://en.wikipedia.org/wiki/Hanafuda) is a kind of traditional Japanese playing cards. A hanafuda deck contains 48 cards divided by 12 suits corresponding to 12 months, which are also divided into four rank-like categories with different importance. [Koi-Koi](https://en.wikipedia.org/wiki/Koi-Koi) is a kind of two-player hanafuda card game. The goal of Koi-Koi is to collect cards by matching the cards by suit, and forming specific winning hands called Yaku from the acquired pile to earn points from the opponent.

![Hanafuda Deck](/markdown/koikoi_deck.png)

## Rules & Yaku List

Koi-Koi is consisted by multiple rounds and both players start with equal points. In every round, two players discard and draw to pair and collect cards by turn until someone forms Yakus successfully. Then, he can end this round to receive points from the opponent, or claim koi-koi and continues this round to earn more yakus and points. The detailed rules and Yaku list of this project is the same as PC game [KoiKoi-Japan](https://store.steampowered.com/app/364930/KoiKoi_Japan_Hanafuda_playing_cards/) on Steam.

![Yaku List](/markdown/koikoi_yaku.png)


# 対戦を回す前にkoikoigameのpip-installを行う

自作ライブラリをインポートするために`koikoigame`に入り、
```
pip install -e .
```
を行いましょう。これを行ったら次へ進んでください。

# socket通信の回し方

自作AIを用いてAgent側と対戦するとき、または自作AI同士で対戦するときのやりかた(singularity shellに入った後)

1. serverの起動

```
$ cd server
$ python3 server.py
```

2. sample_client.pyの起動(自作AIをsample_client.pyのところに実装してください！)自作AIを実装しなくてもランダムに返すもの同士で対戦はできます

```
$ cd samples
$ python3 sample_client.py
```

その後、
```
Enter mode (1 for playing against AI, 2 for playing against another client): 
```
と聞かれるのでモードを半角数字で入力してください！
モード1はランダムに返すエージェントとの対戦で、2は自作AI同士で対戦できます！

```
Enter number of games to play: 
```
で対戦数を決めます(ゲームを何回やるか)。半角数字で入力してください！

```
Enter your player name: 
```
で名前を入力

ゲームの進捗バーが表示されます。以下は例
```
Singularity> python3 sample_client.py 
Enter mode (1 for playing against AI, 2 for playing against another client): 1
Enter number of games to play: 10
Enter your player name: nunu
Games Progress:   0%|                                                            | 0/10 [00:00<?, ?game/s]Connection established, entering room
Connected to server
Entering room...
Sending enter_room event with data: {'room_id': 123, 'player_name': 'nunu', 'mode': 1, 'num_games': 10}
Games Progress:  10%|█████▏                                              | 1/10 [00:00<00:03,  2.48game/s]Winner of this game: Player 2
```

対戦が終わったら結果が表示されます。以下は例です。
```
Game over. Final results: Games played: 10, nunuWins: 7, AIWins: 3, Draws: 0
Disconnected from server
Winner of this game: Player 1
```

# チーム内向けメモ

## 学習
- `singularity shell --nv --bind $HOME /share/koikoi_organizers/koikoi_3.8.17.sif`
- `python base_models/sl_train.py --w_yaku_loss=1.0 --task_name=discard --epochs=50 --batch=512`

- `task_name`は， `discard`, `pick`, `koikoi` から選択してそれぞれのモデルを学習
