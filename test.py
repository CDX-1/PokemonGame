import socket
import json
import threading

# Rename the socket instance to avoid conflict with the module name
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("127.0.0.1", 3000))

def send(msg):
    server.send(msg.encode('utf-8'))

def send_obj(obj):
    server.send(json.dumps(obj).encode('utf-8'))

battle_id = None

def listen():
    global battle_id
    buffer = ""
    while True:
        data = server.recv(4096)
        if not data:
            break
        buffer += data.decode('utf-8')
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            try:
                obj = json.loads(line.strip())
                if obj["action"] == "create" and "battle_id" in obj:
                    battle_id = obj["battle_id"]
                    print(f"Loaded battle: {battle_id}")
                else:
                    print(obj)
            except json.JSONDecodeError as e:
                print("Failed to decode JSON:", e)

listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

send_obj({ "action": "create" })

while True:
    if battle_id is None:
        continue
    inp = input("> ")
    server.send(json.dumps({"action": "command", "command": f">{inp}", "battle_id": battle_id}).encode('utf-8'))