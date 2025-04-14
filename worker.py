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

def start(host='localhost', port=15000, search_path='.'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print(f"Searching in {path} ...")

    while True:
        data = s.recv(4096)
        if not data:
            break
        message = json.loads(data.decode())
        query = message.get("query")
        if query:
            print(f"[SEARCH] Looking for '{query}' in {search_path}")
            results = search_files(query, search_path)
            s.sendall(json.dumps({"results": results}).encode())

if __name__ == "__main__":
    port = int(sys.argv[1])
    path = sys.argv[2]
    start(port, path)