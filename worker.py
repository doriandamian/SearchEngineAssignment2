import os
import socket
import sys

def search_files(path, query):
    matches = []
    for root, _, files in os.walk(path):
        for f in files:
            if query.lower() in f.lower():
                matches.append(os.path.join(root, f))
    return matches

def start(port, path):
    s = socket.socket()
    s.bind(('localhost', port))
    s.listen(1)
    print(f"Started working on port {port}.")
    print(f"Searching in {path} ...")

    while True:
        conn, _ = s.accept()
        query = conn.recv(1024).decode()

        if query == "__shutdown__":
            print(f"Worker on port {port} shutting down.")
            conn.close()
            break

        results = search_files(path, query)
        conn.sendall('\n'.join(results).encode())
        conn.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    path = sys.argv[2]
    start(port, path)