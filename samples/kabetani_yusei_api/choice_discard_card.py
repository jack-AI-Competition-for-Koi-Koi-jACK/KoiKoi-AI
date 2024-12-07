import time
import random
import numpy as np
import samples.kabetani_yusei_api.yaku as YAKU


class ChoiceDiscardCard:
    def __init__(self):
        pass


    def choice(self, observation, unplayed_card, pile_num, op_hand_num):
        '''
        捨てるカードを選択する
        1. 場のカードを取れる場合は、取れるカードの中で選択
        2. それ以外の場合は、手札のカードすべての中で選択する
        '''
        cand_card = []
        for my_card in observation['your_hand']:
            for field_card in observation['field']:
                if my_card[0] == field_card[0]:
                    cand_card.append(my_card)
                    break
        
        # 場のカードを取れない場合は、手札のカードすべての中で選択
        if len(cand_card) == 0:
            cand_card = observation['your_hand']

        # シミュレーションをして、最も得点が高くなるカードを選択
        res = ([0, 0], -10) # (card, score)
        time_limit = 2.5 / len(cand_card)
        for card in cand_card:
            score = self._simulate(observation, unplayed_card, card, time_limit, pile_num, op_hand_num)
            if score > res[1]:
                res = (card, score)
        return res[0]


    def _simulate(self, observation, unplayed_card, my_card, time_limit, pile_num, op_hand_num):
        '''
        シミュレーションをして、最も得点が高くなるカードを選択
        '''
        # シミュレーション前の用意
        start_time = time.time()
        score = 0
        attempt = 0
        op_pile_original = [[element for element in op_pile_card] for op_pile_card in observation['op_pile']]
        field_original = [[element for element in field_card] for field_card in observation['field']]
        my_hand_original = [[element for element in your_hand_card] for your_hand_card in observation['your_hand']]
        my_pile_original = [[element for element in my_pile] for my_pile in observation['your_pile']]
        unplayed_card_original = [[element for element in unplayed_card_card] for unplayed_card_card in unplayed_card]

        while(time.time() - start_time < time_limit):
            # シミュレーションの初期化
            op_pile = [[element for element in op_pile_card] for op_pile_card in op_pile_original]
            field = [[element for element in field_card] for field_card in field_original]
            my_hand = [[element for element in your_hand_card] for your_hand_card in my_hand_original]
            my_pile = [[element for element in my_pile] for my_pile in my_pile_original]
            unplayed_card = [[element for element in unplayed_card_card] for unplayed_card_card in unplayed_card_original]
            pile, op_hand = self.__create_random_pile_and_hand(unplayed_card, pile_num, op_hand_num)

            '''最初の自分のターン'''
            # カードを捨てる
            discard_card = my_card
            my_hand.remove(discard_card)
            # 場にペアになるカードがあれば取る
            choice_field_card = self.__choice_field_card(field, discard_card)
            if choice_field_card is not None:
                field.remove(choice_field_card)
                my_pile.append(discard_card)
                my_pile.append(choice_field_card)
            else:
                field.append(discard_card)
            # 山札からカードを引く
            pile_card = random.choice(pile)
            pile.remove(pile_card)
            # 場からペアになるカードがある場合は取る
            choice_field_card = self.__choice_field_card(field, discard_card)
            if choice_field_card is not None:
                field.remove(choice_field_card)
                my_pile.append(pile_card)
                my_pile.append(choice_field_card)
            else:
                field.append(pile_card)
            # 終了判定をする
            ## 自分が上がった場合
            point = YAKU.yaku_check(my_pile)
            if point >= 1:
                score += self.__custom_sigmoid(point)
                attempt += 1
                continue
            ## 自分と相手の手札がなくなった場合
            if len(my_hand) == 0 and len(op_hand) == 0:
                attempt += 1
                continue


            '''シミュレーションをする'''
            while(time.time() - start_time < time_limit):
                '''相手のターン'''
                # カードを捨てる
                discard_card = random.choice(op_hand)
                op_hand.remove(discard_card)
                # 場にペアになるカードがあれば取る
                choice_field_card = self.__choice_field_card(field, discard_card)
                if choice_field_card is not None:
                    field.remove(choice_field_card)
                    op_pile.append(discard_card)
                    op_pile.append(choice_field_card)
                else:
                    field.append(discard_card)
                # 山札からカードを引く
                pile_card = random.choice(pile)
                pile.remove(pile_card)
                # 場からペアになるカードがある場合は取る
                choice_field_card = self.__choice_field_card(field, discard_card)
                if choice_field_card is not None:
                    field.remove(choice_field_card)
                    op_pile.append(pile_card)
                    op_pile.append(choice_field_card)
                else:
                    field.append(pile_card)
                # 終了判定をする
                ## 相手が上がった場合
                point = YAKU.yaku_check(op_pile)
                if point >= 1:
                    score += self.__custom_sigmoid(-point)
                    attempt += 1
                    break
                ## 自分と相手の手札がなくなった場合
                if len(my_hand) == 0 and len(op_hand) == 0:
                    attempt += 1
                    break

                '''自分のターン'''
                # カードを捨てる
                discard_card = random.choice(my_hand)
                my_hand.remove(discard_card)
                # 場にペアになるカードがあれば取る
                choice_field_card = self.__choice_field_card(field, discard_card)
                if choice_field_card is not None:
                    field.remove(choice_field_card)
                    my_pile.append(discard_card)
                    my_pile.append(choice_field_card)
                else:
                    field.append(discard_card)
                # 山札からカードを引く
                pile_card = random.choice(pile)
                pile.remove(pile_card)
                # 場からペアになるカードがある場合は取る
                choice_field_card = self.__choice_field_card(field, discard_card)
                if choice_field_card is not None:
                    field.remove(choice_field_card)
                    my_pile.append(pile_card)
                    my_pile.append(choice_field_card)
                else:
                    field.append(pile_card)
                # 終了判定をする
                ## 自分が上がった場合
                point = YAKU.yaku_check(my_pile)
                if point >= 1:
                    score += self.__custom_sigmoid(point)
                    attempt += 1
                    break
                ## 自分と相手の手札がなくなった場合
                if len(my_hand) == 0 and len(op_hand) == 0:
                    attempt += 1
                    break
        # print("is check")
        # print(my_card, score, attempt, score / attempt)
        return score / attempt

    def __create_random_pile_and_hand(self, unplayed_card, pile_num, op_hand_num):
        '''
        未使用のカードからランダムに山札と手札を作成する
        '''
        # 一度に必要なカードを全てランダム選択
        total_cards_needed = pile_num + op_hand_num
        selected_cards = random.sample(unplayed_card, total_cards_needed)

        # 最初の pile_num 枚を山札、次の op_hand_num 枚を手札に分ける
        pile = selected_cards[:pile_num]
        hand = selected_cards[pile_num:]
        return pile, hand


    def __choice_field_card(self, field, discard_card):
        '''
        場のカードから取るカードを選択する
        取れるカードがない場合はNoneを返す
        '''
        valid_field_card = []
        for field_card in field:
            if field_card[0] == discard_card[0]:
                valid_field_card.append(field_card)
        return random.choice(valid_field_card) if len(valid_field_card) > 0 else None


    def __custom_sigmoid(self, x):
        '''
        シグモイド関数っぽいやつ(xを4で割っている)
        '''
        return 2 / (1 + np.exp(-(x / 4))) - 1


# if __name__ == "__main__":
#     observation = {'turn': 1, 'state': 'discard', 'op_total_point': 0, 'op_yaku': [], 'op_Light': [], 'op_Seed': [], 'op_Ribbon': [], 'op_Dross': [], 'op_pile': [], 'field': [[1, 1], [2, 2], [3, 2], [6, 3], [7, 2], [10, 3], [10, 4], [12, 1]], 'your_hand': [[3, 3], [6, 1], [9, 2], [9, 3], [10, 2], [11, 4], [12, 3], [12, 4]], 'your_yaku': [], 'your_Light': [], 'your_Seed': [], 'your_Ribbon': [], 'your_Dross': [], 'your_total_point': 0, 'koikoi': {'1': [0, 0, 0, 0, 0, 0, 0, 0], '2': [0, 0, 0, 0, 0, 0, 0, 0]}, 'show': [], 'legal_action': [[3, 3], [6, 1], [9, 2], [9, 3], [10, 2], [11, 4], [12, 3], [12, 4]], 'your_pile': []}
#     unplayed_card = [[1, 2], [1, 3], [1, 4], [2, 1], [2, 3], [2, 4], [3, 1], [3, 4], [4, 1], [4, 2], [4, 3], [4, 4], [5, 1], [5, 2], [5, 3], [5, 4], [6, 2], [6, 4], [7, 1], [7, 3], [7, 4], [8, 1], [8, 2], [8, 3], [8, 4], [9, 1], [9, 4], [10, 1], [11, 1], [11, 2], [11, 3], [12, 1], [13, 1], [13, 2], [13, 3], [13, 4]]
#     cd = ChoiceDiscardCard()
#     res = cd.choice(observation, unplayed_card, 24, 8)
#     print(res)