import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from natsort import natsorted
import re
from glob import glob

from tqdm import tqdm

import koikoigame.koikoigame as koikoiganme
from koikoigame.koikoigame import KoiKoiCard


def list_to_tuple(nested_list):
    if isinstance(nested_list, list):
        return tuple(list_to_tuple(item) for item in nested_list)
    return nested_list


def get_winner_yaku(filename: str):
    json_open = open(f"{filename}", "r")
    json_load = json.load(json_open)

    results = []
    for round in range(1, 9):
        if "round" f"{round}" not in json_load["record"].keys():
            break
        winner_card = []
        winner = json_load["record"]["round" f"{round}"]["basic"]["roundWinner"]
        turn = 1
        while True:
            if (
                json_load["record"]["round" f"{round}"]["turn" f"{turn}"][
                    "playerInTurn"
                ]
                == winner
            ):
                collectCard = json_load["record"]["round" f"{round}"]["turn" f"{turn}"][
                    "collectCard"
                ]
                collectCard2 = json_load["record"]["round" f"{round}"][
                    "turn" f"{turn}"
                ]["collectCard2"]
                winner_card.extend(list_to_tuple(collectCard))
                winner_card.extend(list_to_tuple(collectCard2))
            if (
                json_load["record"]["round" f"{round}"]["turn" f"{turn}"]["isKoiKoi"]
                == False
                or turn == 16
            ):  # 最長でturn16までしかいかない
                break
            turn += 1
        # print(winner_card)
        winner_yaku = []
        winner_yaku.extend(get_yaku(winner_card))
        # print(winner_yaku)
        results.append(winner_yaku)
    return results


def get_yaku(pile: list):
    koikoi_num = 0  # ひとまずこの値を無視
    yaku = []
    # pile = set([tuple(card) for card in self.pile[player]])
    # koikoi_num = self.koikoi_num[player]
    pile = set(pile)
    num_light = len(pile & KoiKoiCard.light)
    if num_light == 5:
        yaku.append((1, "Five Lights", 10))
    elif num_light == 4 and (11, 1) not in pile:
        yaku.append((2, "Four Lights", 8))
    elif num_light == 4:
        yaku.append((3, "Rainy Four Lights", 7))
    elif num_light == 3 and (11, 1) not in pile:
        yaku.append((4, "Three Lights", 5))

    num_seed = len(pile & KoiKoiCard.seed)
    if KoiKoiCard.boar_deer_butterfly.issubset(pile):
        yaku.append((5, "Boar-Deer-Butterfly", 5))
    if KoiKoiCard.flower_sake.issubset(pile) and koikoi_num == 0:
        yaku.append((6, "Flower Viewing Sake", 1))
    elif KoiKoiCard.flower_sake.issubset(pile) and koikoi_num > 0:
        yaku.append((7, "Flower Viewing Sake", 3))
    if KoiKoiCard.moon_sake.issubset(pile) and koikoi_num == 0:
        yaku.append((8, "Moon Viewing Sake", 1))
    elif KoiKoiCard.moon_sake.issubset(pile) and koikoi_num > 0:
        yaku.append((9, "Moon Viewing Sake", 3))
    if num_seed >= 5:
        yaku.append((10, "Tane", num_seed - 4))

    num_ribbon = len(pile & KoiKoiCard.ribbon)
    if (KoiKoiCard.red_ribbon | KoiKoiCard.blue_ribbon).issubset(pile):
        yaku.append((11, "Red & Blue Ribbons", 10))
    if KoiKoiCard.red_ribbon.issubset(pile):
        yaku.append((12, "Red Ribbons", 5))
    if KoiKoiCard.blue_ribbon.issubset(pile):
        yaku.append((13, "Blue Ribbons", 5))
    if num_ribbon >= 5:
        yaku.append((14, "Tan", num_ribbon - 4))

    num_dross = len(pile & KoiKoiCard.dross)
    if num_dross >= 10:
        yaku.append((15, "Kasu", num_dross - 9))

    # if koikoi_num > 0:
    #     yaku.append((16, "Koi-Koi", koikoi_num))

    return yaku


def extract_file_number(file_path):
    return int(re.search(r"(\d+)", file_path).group())


if __name__ == "__main__":
    #     filename = "/home/kaz/KoiKoi-AI/gamerecords_dataset/1.json"
    #     yaku_list = get_winner_yaku(filename)
    #     print(f"yaku_list {yaku_list}")
    files = glob("/home/kaz/KoiKoi-AI/gamerecords_dataset/*.json")
    # ここで，filesをソートする
    # ただし，ファイル名の数字の順番に並ぶようにして!!!! → Done
    files = sorted(files, key=extract_file_number)

    output_file = "yaku_results.csv"
    yakus = [
        "Five Lights",
        "Four Lights",
        "Rainy Four Lights",
        "Three Lights",
        "Boar-Deer-Butterfly",
        "Flower Viewing Sake",
        "Flower Viewing Sake",
        "Moon Viewing Sake",
        "Moon Viewing Sake",
        "Tane",
        "Red & Blue Ribbons",
        "Red Ribbons",
        "Blue Ribbons",
        "Tan",
        "Kasu",
    ]
    with open(output_file, "w") as f_out:
        for i in range(len(yakus)):
            f_out.write(yakus[i])
            f_out.write(",")
        f_out.write("\n")

        for file in tqdm(files):
            # 役取得
            file_yaku = get_winner_yaku(file)
            for round in range(len(file_yaku)):
                round_results = [0 for _ in range(15)]
                for i_yaku in range(len(file_yaku[round])):
                    round_results[file_yaku[round][i_yaku][0] - 1] = 1
                # csvに書き込む
                for i in range(len(round_results)):
                    f_out.write(str(round_results[i]))
                    f_out.write(",")
                f_out.write("\n")
