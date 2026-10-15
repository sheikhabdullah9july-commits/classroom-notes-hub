import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Run with SocketIO for real-time chat
    socketio.run(app, debug=os.environ.get('FLASK_DEBUG') == '1', host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)

