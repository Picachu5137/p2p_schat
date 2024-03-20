import socket
import ssl
import threading


class Client:
    TCP_MAX_SIZE = 4096

    def __init__(self, ip: str = "127.0.0.1", port: int = 2424):
        self.sock_l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_l.bind((ip, port))

        self.sock_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected_addresses = []

    def listen(self):
        msg, addr = self.sock_l.recvfrom(Client.TCP_MAX_SIZE)

        if addr in self.connected_addresses:
            pass  # TODO: сделать приём сообщений с сокета self.sock_l

    def connect(self, host: str = "127.0.0.1", port: int = 2424):
        self.sock_c.connect((host, port))
        self.connected_addresses.append((host, port))


if __name__ == "__main__":
    cli = Client()
