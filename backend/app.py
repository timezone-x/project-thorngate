import re
import time
from asyncio.windows_events import NULL

from flask import Flask, render_template, redirect, jsonify
from mcstatus import JavaServer
from pathlib import Path
import json

app = Flask(__name__)
servers_cache = {"data": None, "timestamp": 0}
services_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 30


class Configs:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.configs = self.load_configs()
        self.services_path = self.configs.get("services_path")



    def load_configs(self):
        with open(self.config_path, "r") as f:
            config = json.load(f)
            return config



class Services:
    def __init__(self):
        pass

    def load_services(self):
        services_path = configs_handler.services_path
        with open(services_path, "r") as f:
            services = json.load(f)
            self.services = services
            self.minecraft_servers = [s for s in services if s['type'] == 'mc-server']
            self.sites = [s for s in services if s['type'] == 'site']
            print(f"services loaded: {services}")
            print(f"minecraft servers loaded: {self.minecraft_servers}")
            print(f"sites loaded: {self.sites}")


    def get_minecraft_servers(self):
        now = time.time()
        if now - servers_cache["timestamp"] < CACHE_TTL:
            return servers_cache["data"]

        servers = self.minecraft_servers
        servers_list = []
        for server in servers:
            data = {}
            name = server['name']
            edition = server['edition']
            public_ip = server['public-ip']
            public_port = server['public-port']
            online = False

            try:
                server = JavaServer.lookup("192.168.0.27")
                status = server.status()
                player_list = []
                if status.players.sample:
                    for player in status.players.sample:
                        player_list.append({"name": player.name, "uuid": player.uuid})

                online = True
                player_count = status.players.online
                max_players = status.players.max
                motd = status.description
                data = {
                    "name": name,
                    "edition": edition,
                    "public_ip": public_ip,
                    "public_port": public_port,
                    "online": online,
                    "player_count": player_count,
                    "max_players": max_players,
                    "motd": motd
                }


            except Exception as e:
                data = {
                    "name": name,
                    "edition": edition,
                    "public_ip": public_ip,
                    "public_port": public_port,
                    "online": online,
                    "error": str(e)
                }

            servers_list.append(data)

        servers_cache["data"] = servers_list
        servers_cache["timestamp"] = now
        print(servers_cache)
        return servers_cache


    def get_services(self):
        now = time.time()
        if now - services_cache["timestamp"] < CACHE_TTL:
            return services_cache["data"]

        services_cache["data"] = self.services
        servers_cache["timestamp"] = now
        return services_cache



    def get_sites(self):


configs_handler = Configs("config.json")
services_handler= Services()

services_handler.load_services()
@app.route('/')
@app.route('/index')
@app.route('/homepage')
def index():  # put application's code here
    return "hello world"


@app.route('/api/servers')
def get_servers():
    servers = services_handler.get_minecraft_servers()
    return jsonify(servers)


@app.route('/api/services')
def get_services():
    services = services_handler.get_services()
    return jsonify(services)

if __name__ == '__main__':
    app.run(debug=True)