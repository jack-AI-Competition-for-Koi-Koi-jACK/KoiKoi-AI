# 方針

![M_STATE](#M_STATE)を利用してカードの彼我の取得確率を計算する．
計算した取得確率から役の成立までの（仮想）距離を計算する．

敵が成立距離が近い役があるとき成立を妨害する．

# M_STATE

各月ごとに考える状態. 
各5状態のその月の札が何枚あるかという数字の組．各5状態とは 自身の手札，場札，自身の取札, 不明，相手の取札
である．

例えば2月の札が2枚手札にあり，2枚が不明な場合， 2月のM_STATEは (2,0,0,2,0)

# 流れ

   observation: Object
-> _observation = Observation(observation)
   パーサ.
-> cardProbTable = CardProbTable(obs)
   Observationを元に取得確率を計算，取得する．
   hold, pickの再設定 (pairのapply)にあたって確率は再計算する．
-> roleProbTable = RoleProbTable(cardProbTable)