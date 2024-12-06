import random
from kabetani_yusei_api.unplayed_card_finder import UnplayedCardFinder
from kabetani_yusei_api.choice_discard_card import ChoiceDiscardCard
from kabetani_yusei_api.choice_pick_card import ChoicePickCard
from kabetani_yusei_api.calculate_card_num import CalculateCardNum

UNPLAYED_CARD_FINDER = UnplayedCardFinder()
DISCARD_API = ChoiceDiscardCard()
PICK_API = ChoicePickCard()
CALCULATE_CARD_NUM = CalculateCardNum()

class KabetaniYuseiAPI:
    def __init__(self):
        pass

    def action(self, observation):
        # 何も選べない場合はNoneを返す
        if observation['legal_action'] == [None]:
            return None
        # こいこいをしない
        if observation['state'] == 'koikoi':
            return False
        # your_pileを作成する
        your_pile = []
        your_pile += observation['your_yaku']
        your_pile += observation['your_Light']
        your_pile += observation['your_Seed']
        your_pile += observation['your_Ribbon']
        your_pile += observation['your_Dross']
        observation['your_pile'] = your_pile

        '''
        'discard', 'discard-pick', 'draw', 'draw-pick'で場合分けする
        'draw'に関しては、何も選べないのでNoneが返される
        'discard-pick'と'draw-pick'に関しては、同じ処理を行えるはず
        'discard', 'discard-pick', 'draw-pick'に対してはモンテカルロ法により決める
        '''
        # 未使用のカードを探す
        unplayed_card = UNPLAYED_CARD_FINDER.find(observation)
        pile_num, op_hand_num = CALCULATE_CARD_NUM.calculate(observation)
        # stateに応じて行動を決定する
        if observation['state'] == 'discard':
            return DISCARD_API.choice(observation, unplayed_card, pile_num, op_hand_num)

        elif observation['state'] == 'discard-pick' or observation['state'] == 'draw-pick':
            return PICK_API.choice(observation, unplayed_card, pile_num, op_hand_num)