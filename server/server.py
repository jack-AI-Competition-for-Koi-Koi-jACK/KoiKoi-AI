import sys
import os
import socketio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import eventlet
from koikoigame.koikoigame.koikoigame import KoiKoiGameState
import random
from koikoigame.koikoigame.koikoiagent import Agent 
sio = socketio.Server()
app = socketio.WSGIApp(sio)

rooms = {}

# 接続時
@sio.event(namespace='/koi-koi')
def connect(sid, environ):
    print('Client connected:', sid)
    sio.emit('connection_established', room=sid, namespace='/koi-koi')

# 切断時
@sio.event(namespace='/koi-koi')
def disconnect(sid):
    print('Client disconnected:', sid)

# モードが1またはルームが二人になったら始める
@sio.on('enter_room', namespace='/koi-koi')
def enter_room(sid, data):
    print(f"Sending enter_room event with data: {data}")  # デバッグ出力
    room_id = data['room_id']
    player_name = data['player_name']
    mode = data['mode']
    num_games = data.get('num_games', 1)
    
    if room_id not in rooms:
        rooms[room_id] = {'players': [], 'game': None, 'mode': mode, 'num_games': num_games}
    
    if len(rooms[room_id]['players']) < 2:
        rooms[room_id]['players'].append((sid, player_name))
        print(f'{player_name} entered room {room_id}')
        sio.enter_room(sid, room_id, namespace='/koi-koi')

        if (mode == 1 and len(rooms[room_id]['players']) == 1) or (mode == 2 and len(rooms[room_id]['players']) == 2):
            start_game(room_id)
    else:
        print(f"Room {room_id} is full. Cannot add more players.")
        sio.emit('room_full', room=sid, namespace='/koi-koi')
        
@sio.on('action', namespace='/koi-koi')
def on_action(sid, data):
    room_id = data['room_id']
    action = data['action']
    game = rooms[room_id]['game']

    if game:
        print(f"Current game state: {game.round_state.state}")  # 現在の状態をログに記録
        if game.round_state.state not in ['discard', 'discard-pick', 'draw', 'draw-pick', 'koikoi']:
            print(f"Invalid game state: {game.round_state.state}")  # 無効な状態をログに記録
            return  # 無効な状態の場合、ステップを実行しない
        game.round_state.step(action)
        if not game.game_over:
            next_player = game.round_state.turn_player
            ask_for_action(room_id, next_player)
        else:
            end_game(room_id)
    else:
      print(f"Game not found in room {room_id}")
      
def start_game(room_id):
    print(f'Starting game in room {room_id}')
    game = KoiKoiGameState()
    rooms[room_id]['game'] = game
    if 'games_played' not in rooms[room_id]:
        rooms[room_id]['games_played'] = 0
        rooms[room_id]['results'] = {'player 1 wins': 0, 'player 2 wins': 0, 'draws': 0}


    if rooms[room_id]['mode'] == 2:
      player1, player2 = rooms[room_id]['players']
    
    if rooms[room_id]['mode'] == 1:
        # rooms[room_id]['ai_agent'] = KoiKoiAgent()
        # AIプレイヤーを追加
        if len(rooms[room_id]['players']) == 1:  # AIプレイヤーがまだ追加されていない場合
            print("Creating AI agent")
            ai_agent = Agent()
            rooms[room_id]['ai_agent'] = ai_agent
            rooms[room_id]['players'].append((None, 'AI'))
            
    print(f"Players in room: {rooms[room_id]['players']}")
    
    print(f"Starting first turn for player: {game.round_state.turn_player}")
    ask_for_action(room_id, game.round_state.turn_player)

def ask_for_action(room_id, player):
    print(f"Asking for action in room {room_id} for player {player}")
    game = rooms[room_id]['game']
    observation = game.observation
    print(f"Current game state: {game.round_state.state}") 

    if game.round_state.state == 'round-over':
        print("Round is over. Starting a new round or ending the game.")
        start_new_round(room_id)
        return

    if rooms[room_id]['mode'] == 1 and player == 2:
        print("AI's turn")
        ai_agent = rooms[room_id]['ai_agent']
        action = ai_agent.auto_action(observation)
        print(f"AI action: {action}")
        on_action(None, {'room_id': room_id, 'action': action})
    else:
        print("Human player's turn")
        player_sid = next(sid for sid, _ in rooms[room_id]['players'] if sid is not None)
        print(f"Emitting ask_act event to player {player_sid}")
        sio.emit('ask_act', observation, room=player_sid, namespace='/koi-koi')

# roundが終わった時用
def start_new_round(room_id):
    game = rooms[room_id]['game']
    game.new_round()
    
    if game.game_over:
        end_game(room_id)
    else:
        print(f"Starting new round. Current round: {game.round}")
        ask_for_action(room_id, game.round_state.turn_player)
        
def end_game(room_id):
    game = rooms[room_id]['game']
    winner = game.winner
    print(f'Game in room {room_id} ended. Winner: {winner}')
    rooms[room_id]['games_played'] += 1

    if winner == 1:
        rooms[room_id]['results']['player 1 wins'] += 1
    elif winner == 2:
        rooms[room_id]['results']['player 2 wins'] += 1
    else:
        rooms[room_id]['results']['draws'] += 1
    
    # progress bar 用
    for player_sid, _ in rooms[room_id]['players']:
        if player_sid:
            sio.emit('game_over', {'winner': winner}, room=player_sid, namespace='/koi-koi')

    if rooms[room_id]['games_played'] < rooms[room_id]['num_games']:
        print(f"Starting new game. Games played: {rooms[room_id]['games_played']}")
        start_game(room_id)
    else:
        results = rooms[room_id]['results']
        result_str = f"Games played: {rooms[room_id]['num_games']}, {rooms[room_id]['players'][0][1]}Wins: {results['player 1 wins']}, {rooms[room_id]['players'][1][1]}Wins: {results['player 2 wins']}, Draws: {results['draws']}"
        
        for player_sid, _ in rooms[room_id]['players']:
            if player_sid:  # AIプレイヤーの場合、sidがNoneなので除外
                sio.emit('game_over', {'result': result_str, 'winner': winner}, room=player_sid, namespace='/koi-koi')
        
        print(f"All games completed. Final results: {result_str}")
        # ルームをクリーンアップ
        del rooms[room_id]    
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
