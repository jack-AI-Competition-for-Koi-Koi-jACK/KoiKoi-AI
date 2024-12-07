'''
山札と相手のカードであり得る札を計算する
余裕があれば、相手の手札に対して確率も付けたい
'''
class UnplayedCardFinder:
    def __init__(self):
        pass
    

    def find(self, observation):
        '''
        全部のカードから、'op_pile'と'field'と'your_hand'と'show'を取り除いたカードを返す
        '''
        unplayed_card = [[i, j] for i in range(1, 14) for j in range(1, 5)]
        # remove op_pile
        for card in observation['op_pile']:
            if card in unplayed_card:
                unplayed_card.remove(card)
        # remove field
        for card in observation['field']:
            if card in unplayed_card:
                unplayed_card.remove(card)
        # remove your_hand
        for card in observation['your_hand']:
            if card in unplayed_card:
                unplayed_card.remove(card)
        # remove show
        for card in observation['show']:
            if card in unplayed_card:
                unplayed_card.remove(card)
        return unplayed_card