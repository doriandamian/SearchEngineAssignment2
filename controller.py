import subprocess
import socket
import time
import difflib
import os

START_PORT = 5000

def get_home_folders():
    home = os.path.expanduser("~")
    return [
        os.path.join(home, d) 
        for d in os.listdir(home) 
            if os.path.isdir(os.path.join(home, d)) and not d.startswith(".")
        ]

def deploy_workers(start_port=START_PORT):
    folders = get_home_folders()
    workers = []

    for i, folder in enumerate(folders):
        port = start_port + i
        subprocess.Popen(["python", "worker.py", str(port), folder])
        workers.append({"port": port, "path": folder})

    return workers

if __name__ == "__main__":
    print("Deploying workers ...")
    workers = deploy_workers()
    print(f"Deployed {len(workers)} workers.")

    time.sleep(1)