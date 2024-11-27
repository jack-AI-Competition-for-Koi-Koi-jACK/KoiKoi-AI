import numpy as np
import random
import pprint
from koikoigame.koikoigame import KoiKoiGameState
import tqdm


class Agent:
    def __init__(self):

        pass

    def auto_action(self, observation):
        legal_action = observation["legal_action"]
        
        

        chosen_action = random.choice(legal_action)
        print(f"AI chose action: {chosen_action} from legal actions: {legal_action}")
        return chosen_action


class Arena:
    def __init__(self, agent_1, agent_2, game_state_kwargs={}):
        """
        agentを戦わせる
        -----------------------------
        入力 :
            agent_1 : エージェント1
            agent_2 : エージェント2
            game_state_kwaegs : dict
        出力 :
            無し
        """

        self.agent_1 = agent_1
        self.agent_2 = agent_2
        self.game_state_kwargs = game_state_kwargs

        self.test_point = {1: [], 2: []}
        self.test_winner = []

    def multi_game_test(self, num_game, clear_result=True):
        """
        ゲームの勝率を計算するメソッド

        """

        def n_count(l, x):
            """
            入力 :
                 l : list
                 x : int
            出力  :
                 float
            """

            return np.sum(np.array(l) == x)

        if clear_result:
            self.clear_test_result()
        for ii in tqdm.tqdm(range(num_game)):
            self.__duel()
        self.test_win_num = [n_count(self.test_winner, ii) for ii in [0, 1, 2]]
        self.test_win_rate = [n / sum(self.test_win_num) for n in self.test_win_num]
        return

    def __duel(self):
        """
        ai vs ai
        """

        self.game_state = KoiKoiGameState(**self.game_state_kwargs)
        while True:
            if self.game_state.game_over == True:
                break
            elif self.game_state.round_state.round_over == True:
                self.game_state.new_round()
            else:
                if self.game_state.round_state.turn_player == 1:
                    action = self.agent_1.custom_act(self.game_state.observation)
                    self.game_state.round_state.step(action)
                else:
                    action = self.agent_2.custom_act(self.game_state.observation)
                    self.game_state.round_state.step(action)
        self.test_point[1].append(self.game_state.point[1])
        self.test_point[2].append(self.game_state.point[2])
        self.test_winner.append(self.game_state.winner)
        return

    def test_result_str(self):
        """
        対戦のテスト結果を出力するためのメソッド
        """
        assert len(self.test_winner) > 0
        win_num = self.test_win_num
        win_rate = self.test_win_rate
        s = f"{sum(win_num)} games tested, "
        s += f"{win_num[1]} wins, {win_num[2]} loses, {win_num[0]} draws "
        s += f"({win_rate[1]:.2f}, {win_rate[2]:.2f}, {win_rate[0]:.2f}), "
        s += f"{np.mean(self.test_point[1]):.1f} points"
        return s

    def clear_test_result(self):
        self.test_point = {1: [], 2: []}
        self.test_winner = []
        return


if __name__ == "__main__":
    agent1 = Agent()
    agent2 = Agent()

    arena = Arena(agent1, agent2)
    arena.multi_game_test(2000)
    print(arena.test_result_str())
