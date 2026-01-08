import socket
from _thread import *
import sys
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '0.0.0.0'
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
    global pos, game_started, clients, player_sockets, player_count, it_player_id

    #save connection
    player_sockets[player_id] = conn
    #send player their id
    conn.send(str(player_id).encode())

    while True:
        try:
            data = conn.recv(2048)
            if not data:
                break
            reply = data.decode('utf-8')
            print(f"Received from player {player_id}: {reply}")

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
                reply_data = f"{pos[other_id]}|{it_player_id}"
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
