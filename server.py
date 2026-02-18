from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, async_mode="gevent")

players = {}  # sid -> dict


def broadcast():
    socketio.emit("player_list", {"players": list(players.values())})


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def on_join(data):
    players[request.sid] = {
        "name": data["name"],
        "emoji": data["emoji"],
        "going": False,
        "restaurant": "",
        "menu": "",
    }
    broadcast()


@socketio.on("update")
def on_update(data):
    sid = request.sid
    if sid in players:
        players[sid]["going"]      = data.get("going", False)
        players[sid]["restaurant"] = data.get("restaurant", "")
        players[sid]["menu"]       = data.get("menu", "")
        broadcast()


@socketio.on("disconnect")
def on_disconnect():
    if request.sid in players:
        del players[request.sid]
        broadcast()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    socketio.run(app, host="0.0.0.0", port=port)
