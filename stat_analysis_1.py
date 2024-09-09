
from itertools import product

# M_STATE:
# 各月ごとに考える状態. 詳説すると，各5状態のその月の札が何枚あるかという数字の組．
# 
# 各5状態とは 自身の手札，場札，自身の取札, 不明，相手の取札
# である．
# 
# 例えば2月の札が2枚手札にあり，2枚が不明な場合， 2月のM_STATEは (2,0,0,2,0)

M_STATE_NODES = [
    (myHand,board,myObtained,unknown,opObtained)
    for myHand, board, myObtained, unknown, opObtained in product(range(0,4+1), repeat=5)
    if myHand+board+myObtained+unknown+opObtained == 4
] 

M_STATE_EDGES = { edges: 0 for edges in product(M_STATE_NODES,M_STATE_NODES)}

from typing import List, Dict
from copy import deepcopy

class TurnState:
    hand: Dict[int, List[List[int]]]
    obtained: Dict[int, List[List[int]]]
    board: List[List[int]]
    pile: List[List[int]]
    def __init__(self, hand1, obtained1, hand2, obtained2, board, pile):
        self.hand = {1: hand1, 2: hand2}
        self.obtained = {1: obtained1, 2: obtained2}
        self.board = board
        self.pile = pile
    def clone(self):
        return TurnState(
            deepcopy(self.hand[1]), 
            deepcopy(self.obtained[1]), 
            deepcopy(self.hand[2]), 
            deepcopy(self.obtained[2]), 
            deepcopy(self.board), 
            deepcopy(self.pile)
        )
    def __call__(self):
        return self.clone()
    def develop(self, player, discard, collected1, draw, collected2):
        # 手札を選ぶ
        self.hand[player].remove(discard)
        self.board.append(discard)
        
        # collected1 != [] なら取得
        for c in collected1: 
            self.board.remove(c)
            self.obtained[player].append(c)
        
        # 山札を引く
        self.pile.remove(draw)
        self.board.append(draw)
        
        # collected2 != [] なら取得
        for c in collected2:
            self.board.remove(c)
            self.obtained[player].append(c)

def make_m_state(turnstate: TurnState):
    m_states = {1:{},2:{}}
    for c in turnstate.hand[1]:
        m_states[1][c[0]] = m_states[1].get(c[0], [0,0,0,0,0])
        m_states[2][c[0]] = m_states[2].get(c[0], [0,0,0,0,0])
        m_states[1][c[0]][0] += 1 #myHand
        m_states[2][c[0]][3] += 1 #unknown
    for c in turnstate.hand[2]:
        m_states[1][c[0]] = m_states[1].get(c[0], [0,0,0,0,0])
        m_states[2][c[0]] = m_states[2].get(c[0], [0,0,0,0,0])
        m_states[1][c[0]][3] += 1 #unknown
        m_states[2][c[0]][0] += 1 #myHand
    for c in turnstate.board:
        m_states[1][c[0]] = m_states[1].get(c[0], [0,0,0,0,0])
        m_states[2][c[0]] = m_states[2].get(c[0], [0,0,0,0,0])
        m_states[1][c[0]][1] += 1 #board
        m_states[2][c[0]][1] += 1 #board
    for c in turnstate.obtained[1]:
        m_states[1][c[0]] = m_states[1].get(c[0], [0,0,0,0,0])
        m_states[2][c[0]] = m_states[2].get(c[0], [0,0,0,0,0])
        m_states[1][c[0]][2] += 1 #myObtained
        m_states[2][c[0]][4] += 1 #opObtained
    for c in turnstate.obtained[2]:
        m_states[1][c[0]] = m_states[1].get(c[0], [0,0,0,0,0])
        m_states[2][c[0]] = m_states[2].get(c[0], [0,0,0,0,0])
        m_states[1][c[0]][4] += 1 #opObtained
        m_states[2][c[0]][2] += 1 #myObtained
    for c in turnstate.pile:
        m_states[1][c[0]] = m_states[1].get(c[0], [0,0,0,0,0])
        m_states[2][c[0]] = m_states[2].get(c[0], [0,0,0,0,0])
        m_states[1][c[0]][3] += 1 #unknown
        m_states[2][c[0]][3] += 1 #unknown
    for p, m in product(range(1, 2+1), range(1,12+1)):
        m_states[p][m] = tuple(m_states[p][m])
    return m_states
        
def mark_transition(from_turnstate: TurnState, to_turnstate: TurnState):
    from_m_state = make_m_state(from_turnstate)
    to_m_state = make_m_state(to_turnstate)
    for p, m in product(range(1, 2+1), range(1,12+1)):
        M_STATE_EDGES[
            from_m_state[p][m], to_m_state[p][m]    
        ] += 1

import json

def remap_to_serialize(dic):
    container = {'container':[]}
    for key in dic:
        container['container'].append(
            {
                'key': key,
                'val': dic[key]
            }
        )
    return container

def remap_to_deserialize(dic):
    result = {}
    for record in dic['container']:
        result[tuple(tuple(k) for k in record['key'])] = record['val']
    return result

try:

    with open('m_state_transition') as f:
        M_STATE_EDGES = remap_to_deserialize(json.load(f))

except FileNotFoundError:

    for i in range(1,202):
        print("progress:",i)
        obj = None
        with open(f"./gamerecords_dataset/{i}.json") as f:
            obj = json.load(f)
        record = obj['record']
        for round in record:
            basic = record[round]['basic']
            init_state = TurnState(basic['initHand1'],[],basic['initHand2'],[],basic['initBoard'],basic['initPile'])
            turn_state = init_state()
            for turn in record[round]:
                if turn == 'basic': continue
                development = record[round][turn]
                next_turn_state = turn_state()
                next_turn_state.develop(
                    development['playerInTurn'],
                    development['discardCard'],
                    development['collectCard'],
                    development['drawCard'],
                    development['collectCard2']
                )
                mark_transition(turn_state, next_turn_state)
                turn_state = next_turn_state

    with open("m_state_transition", "w") as f:
        json.dump(remap_to_serialize(M_STATE_EDGES) ,f)

IMPORTANT_EDGES = [ item
    for item in sorted( M_STATE_EDGES.items(), key=lambda item:item[1] )
    if item[0][0] != item[0][1] and item[1] > 0
]

IMPORTANT_NODES = list(
    {edge[0][0] for edge in IMPORTANT_EDGES}
    |{edge[0][1] for edge in IMPORTANT_EDGES}
)

M_STATE_TRANSIENT_RATIO = {}

for node in IMPORTANT_NODES:
    from_the_node = [edge for edge in IMPORTANT_EDGES if edge[0][0] == node]
    gross_transitions = sum(edge[1] for edge in from_the_node)
    M_STATE_TRANSIENT_RATIO[node] = {
        edge[0][1]: edge[1]/gross_transitions for edge in from_the_node
    }

# 明らかな遷移を追加しておく

M_STATE_TRANSIENT_RATIO[(4,0,0,0,0)] = M_STATE_TRANSIENT_RATIO.get((4,0,0,0,0),{})
M_STATE_TRANSIENT_RATIO[(4,0,0,0,0)][(0,0,4,0,0)] = 1.0

M_STATE_TRANSIENT_RATIO[(0,0,4,0,0)] = {}
M_STATE_TRANSIENT_RATIO[(0,0,0,0,4)] = {}

# それぞれのm_stateから(0,0,0,0,4), (0,0,2,0,2), (0,0,4,0,0)に発展する確率を算出する

M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE = deepcopy(M_STATE_TRANSIENT_RATIO)
M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF = deepcopy(M_STATE_TRANSIENT_RATIO)

modified = True
while modified:
  modified = False
  for primary_state in M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE:
    for secondary_state in M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE[primary_state]:
      if len(M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF[secondary_state].keys()) > 0:
        modified = True
        weight = M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF[primary_state][secondary_state]
        del M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF[primary_state][secondary_state]
        weighted_ratios = {
            trinary_state: weight*M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF[secondary_state][trinary_state]
            for trinary_state in M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF[secondary_state]
        }
        for trinary_state in weighted_ratios:
            M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF[primary_state][trinary_state] \
                = M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF[primary_state].get(
                    trinary_state, 0
                ) + weighted_ratios[trinary_state]
  M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE = deepcopy(M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE_BUF)

print(M_STATE_TRANSIENT_RATIO_TO_TERMINATE_STATE)
            
              