from flask import Flask
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app)

# @socketio.on('new-message')
def handle_message(message):
    print('received message: ' + message)
    socketio.emit('new-message', message)


@socketio.on('connect')
def test_connect():
    handle_message("hey")
    print("helllo")

if __name__ == '__main__':
	socketio.run(app,port=5001)
