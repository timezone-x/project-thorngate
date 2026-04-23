import re
import time
from flask import Flask, render_template, redirect, jsonify
from mcstatus import JavaServer

app = Flask(__name__)
server1_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 30

def get_server1_status():
    now = time.time()
    if now - server1_cache["timestamp"] < CACHE_TTL:
        return server1_cache["data"]

    try:
        server = JavaServer.lookup("192.168.0.27")
        status = server.status()
        player_list = []
        if status.players.sample:
            for player in status.players.sample:
                player_list.append({"name": player.name, "uuid": player.uuid})
        data = {
            "online": True,
            "players_online": status.players.online,
            "max_players": status.players.max,
            "motd": status.description,
            "player_list": player_list
        }
    except Exception as e:
        data = {
            "online": False,
            "error": str(e)
        }

    server1_cache["data"] = data
    server1_cache["timestamp"] = now
    print(data)
    return data


@app.route('/')
@app.route('/index')
@app.route('/homepage')
def index():  # put application's code here
    return "hello world"


@app.route('/api/server1_status')
def server1_status():
    try:
        data = get_server1_status()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
    get_server1_status()