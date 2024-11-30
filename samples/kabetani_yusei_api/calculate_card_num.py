class CalculateCardNum:
    def __init__(self):
        self.first_player = False # 先手かどうか先手-> True 後手-> False

    
    def calculate(self, observation):
        '''
        相手の手札のカード枚数と山札のカード枚数を計算する
        '''
        # 先手についての更新
        self._first_player_check(observation)

        # 相手の手札のカード枚数を計算
        now_turn = observation['turn']
        if self.first_player:
            op_hand_num = 9 - now_turn
            if observation['state'] == 'discard':
                pile_num = 24 - 2 * (now_turn - 1)
            else:
                pile_num = 23 - 2 * (now_turn - 1)
        else:
            op_hand_num = 8 - now_turn
            if observation['state'] == 'discard':
                pile_num = 23 - 2 * (now_turn - 1)
            else:
                pile_num = 22 - 2 * (now_turn - 1)

        return (pile_num, op_hand_num)


    def _first_player_check(self, observation):
        '''
        先手かどうかを判定する
        '''
        if observation['turn'] == 1:
            if len(observation['field']) == 8 and len(observation['op_pile']) == 0:
                self.first_player = True
            else:
                self.first_player = False