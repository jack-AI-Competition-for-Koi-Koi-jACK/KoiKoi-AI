YAKU = {
    ((1, 1), (3, 1), (8, 1), (11, 1), (12, 1)): 10,# 五光
    ((1, 1), (3, 1), (8, 1), (12, 1)): 8,# 四光
    ((6, 1), (7, 1), (10, 1)): 5,# 猪鹿蝶
    ((9, 1), (3, 1)): 1,# 花見酒
    ((9, 1), (8, 1)): 1,# 月見酒
    ((6, 2), (9, 2), (10, 2)): 5,# 青短
    ((1, 2), (2, 2), (3, 2)): 5,# 赤短
    ((1, 2), (2, 2), (3, 2), (6, 2), (9, 2), (10, 2)): 10,# 赤青短
}

FOUR_LIGHTS = {(1, 1), (3, 1), (8, 1), (12, 1)}# 四光
THREE_LIGHTS = {(1, 1), (3, 1), (8, 1), (12, 1)}# 三光
TANE = {(2, 1), (4, 1), (5, 1), (6, 1),
        (7, 1), (8, 2), (9, 1), (10, 1), (11, 2)}# タネ
TAN =   {(1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
        (6, 2), (7, 2), (9, 2), (10, 2), (11, 3)}# タン
KASU = {(1, 3), (1, 4), (2, 3), (2, 4), (3, 3), (3, 4),
        (4, 3), (4, 4), (5, 3), (5, 4), (6, 3), (6, 4),
        (7, 3), (7, 4), (8, 3), (8, 4), (9, 3), (9, 4),
        (10, 3), (10, 4), (11, 4), (12, 2), (12, 3), (12, 4), (9, 1)}# カス

def yaku_check(hand):
    '''
    手札から役の点数を計算する
    '''
    yaku_point = 0

    # 手札をタプル形式に変換（[[9, 2], [10, 3]] -> {(9, 2), (10, 3)}）
    hand_set = set(map(tuple, hand))
    
    # 形が決められている役の確認
    for yaku, point in YAKU.items():
        if set(yaku) <= hand_set:
            yaku_point += point

    # 形が決められていない役の確認 (例: four_lights)
    yaku_point += other_yaku_check(hand_set)

    return yaku_point


def other_yaku_check(hand_set):
    other_yaku_point = 0

    # 四光の確認
    if (11, 1) in hand_set:
        if len(hand_set & FOUR_LIGHTS) >= 3:
            other_yaku_point += 7

    # 三光の確認
    if len(hand_set & THREE_LIGHTS) >= 3:
        other_yaku_point += 5

    # タネの確認
    other_yaku_point += max(0, len(hand_set & TANE) - 4)

    # タンの確認
    other_yaku_point += max(0, len(hand_set & TAN) - 4)

    # カスの確認
    other_yaku_point += max(0, len(hand_set & KASU) - 9)

    return other_yaku_point