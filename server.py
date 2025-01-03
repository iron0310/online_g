from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# 소켓 이벤트 처리 예시
@socketio.on('message')
def handle_message(message):
    print('받은 메시지:', message)
    # 클라이언트로 메시지 보내기
    socketio.emit('message', '서버로부터 메시지')

if __name__ == '__main__':
    socketio.run(app)
