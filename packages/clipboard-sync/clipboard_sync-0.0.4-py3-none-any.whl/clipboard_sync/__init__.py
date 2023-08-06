import os
import typing as t
import time
import threading
import socket
import subprocess
import argparse
from distutils.spawn import find_executable


copy_cmd = []
paste_cmd = []

if find_executable("xsel"):
    copy_cmd = ["xsel", "-i"]
    paste_cmd = ["xsel", "-o"]
elif find_executable("xclip"):
    copy_cmd = ["xclip", "-i"]
    paste_cmd = ["xclip", "-o"]
elif find_executable("pbcopy"):
    copy_cmd = ["pbcopy"]
    paste_cmd = ["pbpaste"]

if not copy_cmd:
    print("No clipboard command found. Please install xsel or xclip.")
    exit(1)


parser = argparse.ArgumentParser(description="Clipboard Synchronizer")

parser.add_argument(
    "--remote-host", type=str, default="dev", help="Remote host to connect to"
)
parser.add_argument(
    "--remote-port", type=int, default=5557, help="Remote port to connect to"
)
parser.add_argument(
    "--host", type=str, default="0.0.0.0", help="Local host to listen on"
)
parser.add_argument("--port", type=int, default=5556, help="Local port to listen on")
parser.add_argument("--display", type=str, default="", help="Display to use")


lock = threading.Lock()
latest_value = ""


class ClipboardSender(threading.Thread):
    def __init__(self, remote_host: str, remote_port: int, *, period: float = 1.0):
        super().__init__()
        self._remote_host = remote_host
        self._remote_port = remote_port
        self._period = period
        self._stopping = False

    def run(self):
        global latest_value
        socket_: t.Optional[socket.socket] = None

        while not self._stopping:

            while socket_ is None:
                socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    socket_.connect((self._remote_host, self._remote_port))
                except ConnectionError:
                    socket_.close()
                    socket_ = None
                    time.sleep(self._period)

            pasted_value = subprocess.run(
                paste_cmd, stdout=subprocess.PIPE
            ).stdout.decode("utf-8")

            with lock:
                if pasted_value != latest_value:
                    try:
                        socket_.sendall(pasted_value.encode())
                        print(f"Sent: {pasted_value}")
                        latest_value = pasted_value
                    except ConnectionError as e:
                        socket_.close()
                        socket_ = None
                        print(f"Connection error: {e}")

            time.sleep(self._period)

    def stop(self):
        self._stopping = True


class ClipboardReceiver(threading.Thread):
    def __init__(self, host: str, port: int, *, period=1.0):
        super().__init__()
        self._host = host
        self._port = port
        self._period = period
        self._stopping = False

    def run(self):
        global latest_value
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))
            s.listen(5)
            while not self._stopping:
                clientsocket, addr = s.accept()
                print(f"Connected to {addr}")
                with clientsocket:
                    while not self._stopping:
                        data = clientsocket.recv(1024)
                        if not data:
                            break
                        received_value = data.decode()
                        with lock:
                            if received_value != latest_value:
                                subprocess.run(copy_cmd, input=received_value.encode())
                                latest_value = received_value
                                print(f"Received: {received_value}")
                        time.sleep(self._period)

    def stop(self):
        self._stopping = True


def main():
    args = parser.parse_args()
    if args.display:
        os.environ["DISPLAY"] = args.display
    sender = ClipboardSender(args.remote_host, args.remote_port)
    receiver = ClipboardReceiver(args.host, args.port)
    receiver.start()
    sender.start()
    print("Watching clipboard...")
    print("Press Ctrl+C to stop.")


if __name__ == "__main__":
    main()
