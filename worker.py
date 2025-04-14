import os
import socket
import sys
import json

def search_files(path, query):
    matches = []
    for root, _, files in os.walk(path):
        for f in files:
            if query.lower() in f.lower():
                matches.append(os.path.join(root, f))
    return matches

def start(host='localhost', port=5050, search_path='.'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print(f"[WORKER] Searching in {path} ...")

    while True:
        data = s.recv(4096)
        if not data:
            break
        message = json.loads(data.decode())
        query = message.get("query")
        if query:
            print(f"[WORKER] Looking for '{query}' in {search_path}")
            results = search_files(search_path, query)
            print(f"[WORKER] Found {len(results)} matches in {search_path}. Sending back to controller.")
            msg = json.dumps({"results": results}).encode()
            msg_len = len(msg).to_bytes(4, byteorder="big")
            s.sendall(msg_len + msg)

if __name__ == "__main__":
    path = sys.argv[1]
    start(search_path=path)