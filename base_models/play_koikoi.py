#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 23:58:43 2021

@author: guansanghai
"""

import os
from koikoigame.koikoigame import KoiKoiGameState
from koikoilearn import AgentForTest

# import koikoigui as gui
import torch  # 1.8.1

# # Demo for playing 8-round koi-koi games vs trained AI
# your_name = 'Player'
# ai_name = 'RL-Point' # 'SL', 'RL-Point', 'RL-WP'
# record_path = 'gamerecords_player/'

# #
# assert ai_name in ['RL-Point','RL-WP','SL']
# record_fold = record_path + ai_name + '/'

# for path in [record_path, record_fold]:
#     if not os.path.isdir(path):
#         os.mkdir(path)

# if ai_name == 'SL':
#     discard_model_path = 'model_agent/discard_sl.pt'
#     pick_model_path = 'model_agent/pick_sl.pt'
#     koikoi_model_path = 'model_agent/koikoi_sl.pt'
# elif ai_name == 'RL-Point':
#     discard_model_path = 'model_agent/discard_rl_point.pt'
#     pick_model_path = 'model_agent/pick_rl_point.pt'
#     koikoi_model_path = 'model_agent/koikoi_rl_point.pt'
# elif ai_name == 'RL-WP':
#     discard_model_path = 'model_agent/discard_rl_wp.pt'
#     pick_model_path = 'model_agent/pick_rl_wp.pt'
#     koikoi_model_path = 'model_agent/koikoi_rl_wp.pt'

# game_state = KoiKoiGameState(player_name=[your_name,ai_name],
#                              record_path=record_fold,
#                              save_record=True)

# discard_model = torch.load(discard_model_path, map_location=torch.device('cpu'))
# pick_model = torch.load(pick_model_path, map_location=torch.device('cpu'))
# koikoi_model = torch.load(koikoi_model_path, map_location=torch.device('cpu'))

# ai_agent = AgentForTest(discard_model, pick_model, koikoi_model)

# TODO: GUI部分を削除してコマンドラインで動けるように頑張る
# window = gui.InitGUI()
# window = gui.UpdateGameStatusGUI(window, game_state)


def print_game_status(game_state):
    print(f"Round: {game_state.round} / {game_state.round_total}")
    print(
        f"{game_state.player_name[1]}: {game_state.point[1]} points,{game_state.player_name[2]}: {game_state.point[2]} points "
    )
    print("-----------------------------------------------")


# def print_board(game_state):
#     round_state = game_state.round_state
#     print(f"Field: {round_state.field}")
#     print(f"Your Hand: {round_state.hand[1]}")
#     print(f"Your Pile: {round_state.pile[1]}")
#     print(f"Opponent's Pile: {round_state.pile[2]}")
#     print(f"Your Yaku: {[yaku[1] for yaku in round_state.yaku(1)]}")
#     print(f"Opponent's Yaku: {[yaku[1] for yaku in round_state.yaku(2)]}")
#     print("-----------------------------------------------")


def get_player_action(game_state):
    round_state = game_state.round_state
    state = round_state.state

    if state == "discard":
        print("Select a card to discard:")
        for i, card in enumerate(round_state.hand[1]):
            print(f"{i + 1}: {card}")
        while True:
            try:
                choice = int(input("Enter the number of the card: ")) - 1
                if 0 <= choice < len(round_state.hand[1]):
                    return round_state.hand[1][choice]
            except ValueError:
                pass
            print("Invalid choice. Please try again.")

    elif state == "discard-pick" or state == "draw-pick":
        if round_state.wait_action:
            print("Select a card to pair:")
            for i, card in enumerate(round_state.pairing_card):
                print(f"{i + 1}: {card}")
            while True:
                try:
                    choice = (
                        int(input("Enter the number of the card (or 0 to skip): ")) - 1
                    )
                    if choice == -1:
                        return None
                    if 0 <= choice < len(round_state.pairing_card):
                        return round_state.pairing_card[choice]
                except ValueError:
                    pass
                print("Invalid choice. Please try again.")
        return None

    elif state == "koikoi":
        if round_state.wait_action:
            choice = input("Do you want to Koi-Koi? (y/n): ").lower()
            return choice == "y"
        return None

    return None


def main():
    your_name = input("Enter your name: ")
    ai_name = input("Enter oppent name")
    record_path = "gamerecords_player/"

    record_fold = record_path + ai_name + "/"

    for path in [record_path, record_fold]:
        if not os.path.isdir(path):
            os.mkdir(path)

    game_state = KoiKoiGameState(
        player_name=[your_name, ai_name],
        record_path=record_fold,
        save_record=True,
    )

    while True:

        state = game_state.round_state.state
        turn_player = game_state.round_state.turn_player

        if game_state.game_over:
            print("Game Over!")
            print(
                f"Final Score: {game_state.player_name[1]}: {game_state.point[1]}, {game_state.player_name[2]}: {game_state.point[2]}"
            )
            break

        elif state == "round-over":
            print("Round Over!")
            print(
                f"Round Score: {game_state.player_name[1]}: {game_state.round_state.round_point[1]}, {game_state.player_name[2]}: {game_state.round_state.round_point[2]}"
            )
            game_state.new_round()
            print_game_status(game_state)

        else:
            print_game_status(game_state)
            # print_board(game_state)

            if turn_player == 1:
                print("Your turn!")
                action = get_player_action(game_state)
            else:
                print("AI's turn...")
                action = get_player_action(game_state)

            if state == "discard":
                game_state.round_state.discard(action)
            elif state == "discard-pick":
                game_state.round_state.discard_pick(action)
            elif state == "draw":
                game_state.round_state.draw(action)
            elif state == "draw-pick":
                game_state.round_state.draw_pick(action)
            elif state == "koikoi":
                game_state.round_state.claim_koikoi(action)

            print(f"Action taken: {state} - {action}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
