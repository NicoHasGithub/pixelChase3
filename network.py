import socket
from _thread import *
import sys

class Network:
    def __init__(self, host="localhost", port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.id = None
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            #recieve an assigned player ID (1 or 0)
            self.id = int(self.client.recv(2048).decode())
            print(f"Connected to server. Plyer Id: {self.id}")
        except socket.error as e:
            print("Connection error:", e)
            self.id = None

    def send(self, data):
        #format: id:x,y, gets sent to server and recievs other player's pos
        if self.client is None:
            return None
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            print("Send or Recieve error:", e)
            return None