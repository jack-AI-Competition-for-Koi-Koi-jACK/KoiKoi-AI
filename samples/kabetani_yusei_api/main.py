import random
from kabetani_yusei_api.unplayed_card_finder import UnplayedCardFinder
from kabetani_yusei_api.choice_discard_card import ChoiceDiscardCard
from kabetani_yusei_api.choice_pick_card import ChoicePickCard

UNPLAYED_CARD_FINDER = UnplayedCardFinder()
DISCARD_API = ChoiceDiscardCard()
PICK_API = ChoicePickCard()

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

        '''
        'discard', 'discard-pick', 'draw', 'draw-pick'で場合分けする
        'draw'に関しては、何も選べないのでNoneが返される
        'discard-pick'と'draw-pick'に関しては、同じ処理を行えるはず
        'discard', 'discard-pick', 'draw-pick'に対してはモンテカルロ法により決める
        '''
        # 未使用のカードを探す
        unplayed_card = UNPLAYED_CARD_FINDER.find(observation)
        # stateに応じて行動を決定する
        if observation['state'] == 'discard':
            return DISCARD_API.choie(observation, unplayed_card)

        elif observation['state'] == 'discard-pick' or observation['state'] == 'draw-pick':
            return PICK_API.choice(observation, unplayed_card)