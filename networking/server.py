import socket, threading, time


BUFFER_SIZE = 4096


class ClientConnection(threading.Thread):
    def __init__(self, host, port, display_name):
        super().__init__()

        self.socket = socket.socket()
        self.socket.connect((host, port))

        self.running = True
        self._queue = []

        self.display_name = display_name
        # TODO: ADD PING CALCULATION

    def run(self) -> None:
        while self.running:
            while len(self._queue):
                item: str = self._queue.pop()
                self.socket.send(item.encode())

            string = ""
            while data := self.socket.recv(BUFFER_SIZE):
                string += data.decode()

            for sub_string in string.split("\n"):
                self.handle(sub_string)

            time.sleep(1)

    def queue(self, string: str):

        if "\n" in string:

            for sub_string in string.split("\n"):
                self.queue(sub_string)

        else:
            self._queue.append(string)

    def handle(self, string: str):
        return

class ServerConnection(threading.Thread):
    def __init__(self, client: socket.socket, host, port):
        super().__init__()
        self.socket = client
        self.host, self.port = host, port

        self.running = True

        # TODO: ADD PING CALCULATION

    def run(self) -> None:
        while self.running:
            string = ""
            while data := self.socket.recv(BUFFER_SIZE):
                string += data.decode()

    def handle(self, string: str):
        pass


class ConnectionHandler(threading.Thread):
    def __init__(self):
        super().__init__()
        self.socket = socket.socket()
        self.socket.bind(("0.0.0.0", 3333))

        self.running = True

        self.clients = []

    def run(self) -> None:
        self.socket.listen(420)
        print("Listening for connections!")
        while self.running:
            client, addr = self.socket.accept()
            thread = ServerConnection(client, *addr)
            print(f"Accepted connection from: {addr[0]}:{addr[1]}")
            thread.start()
            self.clients.append(thread)

    def __del__(self):
        for client in self.clients:
            client.running = False
