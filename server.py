import socket
from _thread import *
import sys
import time
import json
import os

#json file management
def load_log():
    if not os.path.exists("game_log.json"):
        with open("game_log.json", "w") as f:
            json.dump([], f)
    with open("game_log.json", "r") as f:
        return json.load(f)

def save_games(data):
    with open("game_log.json", "w") as f:
        json.dump(data, f, indent=2)

def add_log(hname, pword):
    data = load_log()
    for game in data:
        if game["host_name"].lower() == hname.lower():
            return False  # Duplicate game
    new_game = {
        "host_name": hname,
        "password": pword,
        "active": True,
        "players_connected": 1
    }
    data.append(new_game)
    save_games(data)
    return True

def join_game_log(hname, pword):
    data = load_log()
    for game in data:
        if game["host_name"].lower() == hname.lower() and game["password"] == pword and game["active"]:
            game["players_connected"] += 1
            if game["players_connected"] >= 2:
                game["active"] = False  # Game ready
            save_games(data)
            return True
    return False
#end of json mgment


active_rooms = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '192.168.0.42'
port = 5555
game_started = False
it_player_id = 0
last_tag_time = 0
tag_cooldown = 2.0 #time in seconds

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

#set the two players positions
pos = ["0:500,200", "1:800,200"]
#store client connections
clients = []
#link player id to a connection
player_sockets = {}

def broadcast_start():
    global clients
    print("Broadcasting START to all clients")
    for i in clients:
        try:
            i.sendall("START".encode())
        except:
            pass

def threaded_client(conn, player_id):
    global pos, game_started, clients, player_sockets, player_count, it_player_id, active_rooms, last_tag_time, tag_cooldown

    #save connection
    player_sockets[player_id] = conn
    #send player their id
    conn.send(str(player_id).encode())

    while True:
        try:
            raw_data = conn.recv(2048)
            if not raw_data:
                break
            reply = raw_data.decode('utf-8')
            print(f"Received from player {player_id}: {reply}")

            #manage game creations
            if reply.startswith("CREATE:"):
                _, name, pword, = reply.split(":")
                success = add_log(name, pword)
                if success:
                    conn.send("OK".encode())
                else:
                    conn.send("ERROR:DUPLICATE".encode())

            #manage search for rooms
            elif reply == "GET_ROOMS":
                log_data = load_log()
                active_games = [g for g in log_data if g["active"]]
                if active_games:
                    g = active_games[0]
                    reply = f"{g['host_name']}:{g['password']}"
                    conn.send(reply.encode())
                else:
                    conn.send("EMPTY".encode())

            elif reply.startswith("JOIN:"):
                _, hname = reply.split(":")
                log_data = load_log()
                success = False
                for game in log_data:
                    if game["host_name"].lower() == hname.lower() and game["active"]:
                        game["players_connected"] += 1
                        if game["players_connected"] >= 2:
                            game["active"] = False
                        save_games(log_data)
                        success = True
                        break
                if success:
                    conn.send("OK".encode())
                else:
                    conn.send("ERROR".encode())

            else:
                #manage  tag request
                global it_player_id

                #error handling "flag"
                send_deafult_reply = True

                if reply.startswith("TAG:"):
                    #player who sent tag request (it) is ID:tag
                    #flip it to other
                    current_time = time.time()
                    tagger_id = int(reply.split(":")[1])


                    if tagger_id == it_player_id and (current_time - last_tag_time) > tag_cooldown:
                        new_it_id = 1- tagger_id
                        it_player_id = new_it_id
                        last_tag_time = current_time
                        print(f"Tag successful: New it player is ID: {it_player_id}")

                #start game if pressed by other player (synchronised)
                elif reply == "START":
                    game_started = True
                    broadcast_start()
                    send_deafult_reply = False
                    continue

                #update pos
                elif reply[0].isdigit():
                    arr = reply.split(":")
                    id = int(arr[0])
                    pos[id] = reply

                #send other player's pos + 'it' ID
                if send_deafult_reply:
                    other_id = 1- player_id
                    current_count = 1
                    log_data = load_log()
                    if log_data:
                        current_count = log_data[-1].get("players_connected", 1)
                    reply_data = f"{pos[other_id]}|{it_player_id}|{current_count}"
                    conn.sendall(reply_data.encode())

        except Exception as e:
            print("Connection error: ", e)
            break

    print(f"Connection with player {player_id} closed")
    pos[player_id] = f"{player_id}:-1,-1"
    conn.close()
    clients.remove(conn)

player_count = 0

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    clients.append(conn)
    start_new_thread(threaded_client, (conn,player_count))
    player_count += 1
