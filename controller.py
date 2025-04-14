import subprocess
import socket
import time
import threading
import json
import os

PORT = 5050

connections = []

def handle_connection(conn, addr):
    print(f"[CONTROLLER] New worker connected at {addr}")
    connections.append(conn)

def get_home_folders():
    home = os.path.expanduser("~")
    return [
        os.path.join(home, d) 
        for d in os.listdir(home) 
            if os.path.isdir(os.path.join(home, d)) and not d.startswith(".")
        ]

def broadcast(query):
    print(f"[CONTROLLER] Sending query: {query}")
    for conn in connections:
        try:
            conn.sendall(json.dumps({"query": query}).encode())
        except Exception as e:
            print(f"[CONTROLLER] Error sending query: {e}")

def recv_all(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def collect():
    results = []
    ready = 0

    while ready < len(connections):
        for conn in connections:
            try:
                raw_len = recv_all(conn, 4)
                if not raw_len:
                    continue
                msg_len = int.from_bytes(raw_len, byteorder="big")
                raw_msg = recv_all(conn, msg_len)
                if raw_msg:
                    result = json.loads(raw_msg.decode())
                    results.extend(result.get("results", []))
                    ready += 1
            except Exception as e:
                print(f"[CONTROLLER] Error receiving from worker: {e}")
                ready += 1  # Prevent blocking forever
    return results

def start_server(host="localhost", port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    print(f"[CONTROLLER] Listening on {host}:{port}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()

def deploy_workers():
    folders = get_home_folders()

    for folder in folders:
        subprocess.Popen(["python", "worker.py", folder])
        time.sleep(0.2)

def rank_results(query, results):
    def score(item):
        name=os.path.basename(item)
        name_lower=name.lower()
        query_lower=query.lower()

        if name == query:
            return 1
        elif name.startswith(query):
            return 2
        elif query in name:
            return 3
        elif query_lower in name_lower:
            return 4
        else:
            return 5
        
    ranks = sorted(results, key=score)
    return ranks

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()

    print("[CONTROLLER] Deploying workers ...")
    workers = deploy_workers()

    while True:
        query = input("Insert file name: ")
        if query:
            broadcast(query)
            results = collect()
            print("\nRESULTS:")
            ranked_results = rank_results(query, results)
            for result in ranked_results[:10]:
                print(result)