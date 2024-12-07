from abc import ABC, abstractmethod


class CustomAgentBase(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def custom_act(self, observation):
        """参加者はこの関数をオーバーライドして行動を実装する"""
        pass

    def act(self, observation):
        try:
            return self.custom_act(observation)
        except:
            legal_actions = observation["legal_action"]
            if len(legal_actions) == 1:
                return legal_actions[0]
            for action in legal_actions:
                if action is None or action is False:
                    return action
            return legal_actions[0]  # デフォルトアクション
