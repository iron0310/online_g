from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from math import sqrt
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# 플레이어 데이터 저장
players = {}
foods = []

# 월드 크기와 음식 최대 개수
WORLD_SIZE = 9000
MAX_FOOD_COUNT = 50



@app.route('/')
def index():
    return render_template('index.html')  # 클라이언트 HTML 파일

# 플레이어 연결 시 처리
@socketio.on('connect')
def handle_connect():
    player_id = request.sid
    players[player_id] = {
        'x': random.randint(100, 9000),  # 초기 위치
        'y': random.randint(100, 9000),
        'size': 10,
        'score': 0
    }
    print(f"Player {player_id} connected.")
    emit('update_players', players, broadcast=True)

# 플레이어 위치 업데이트
@socketio.on('move_player')
def handle_move(data):
    player_id = request.sid
    if player_id in players:
        players[player_id]['x'] = data['x']
        players[player_id]['y'] = data['y']
        socketio.emit('update_players', players)

        
        check_player_collisions()

        # 클라이언트에 업데이트 전송
        
        socketio.emit('update_foods', foods, to='broadcast')


# 플레이어 연결 해제 시 처리
@socketio.on('disconnect')
def handle_disconnect():
    player_id = request.sid
    if player_id in players:
        del players[player_id]
    print(f"Player {player_id} disconnected.")
    emit('update_players', players, broadcast=True)





def check_player_collisions():
    to_remove = []
    for id1, p1 in players.items():
        for id2, p2 in players.items():
            if id1 == id2:
                continue  # 동일 플레이어는 스킵
            dx = p1['x'] - p2['x']
            dy = p1['y'] - p2['y']
            distance = sqrt(dx ** 2 + dy ** 2)

            if distance < p1['size'] + p2['size']:  # 충돌
                if p1['size'] > p2['size']:  # p1이 p2를 먹음
                    p1['size'] += p2['size'] / 2  # p2 크기의 절반만큼 증가
                    p1['score'] += 1
                    to_remove.append(id2)  # p2를 삭제
                elif p1['size'] < p2['size']:  # p2가 p1을 먹음
                    p2['size'] += p1['size'] / 2
                    p2['score'] += 1
                    to_remove.append(id1)

    # 충돌된 플레이어 제거
    for rid in to_remove:
        if rid in players:
            del players[rid]
    socketio.emit('update_players', players)  # 플레이어 정보 업데이트 브로드캐스트


if __name__ == '__main__':
    socketio.run(app, debug=True)
