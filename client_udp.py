import socket
import ssl
import vp
import random


class Client:
    TCP_MAX_SIZE = 4096

    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = 2424, *args, **kwargs):
        self.private_key, self.public_key = vp.generate_keys()

        self.sock_l_port = port
        self.sock_l_ip = ip
        self.sock_l = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_l.bind((ip, port))

        self.sock_c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._connected_addresses = []

    def listen(self, *args, **kwargs):
        encrypted_msg, addr = self.sock_l.recvfrom(Client.TCP_MAX_SIZE)

        if any([addr[0] in peer for peer in self._connected_addresses]):
            if encrypted_msg:
                encrypted_msg = encrypted_msg.decode("utf-8")
                msg = vp.decrypt(encrypted_msg)
                return msg, addr[0]

        else:
            print(f"denied connection from {addr[0]}:{addr[1]}")
        return None, addr[0]

    def connect(self, host: str = "127.0.0.1", port: int = 2424, *args, **kwargs):
        """
        add new peer to connected_addresses
        :param host: ip of peer
        :param port: port of peer
        :param args:
        :param kwargs:
        """
        peer = (host, port)
        self._connected_addresses.append(peer)
        print(f"connected {self._connected_addresses}")

    def send_msg(self, msg: str, host: str, port: int, *args, **kwargs):
        """
        send msg to host with name
        :param msg:
        :param host:
        :param port:
        :param args:
        :param kwargs:
        :return None:
        """
        peer = (host, port)
        e_msg = vp.encrypt(msg)
        self.sock_c.sendto(e_msg.encode("utf-8"), peer)

    def disconnect(self, host: str, *args, **kwargs):
        msg = vp.encrypt(f"peer {self.sock_l_ip}:{self.sock_l_port} abort the connection").encode("utf-8")
        self.sock_c.sendto(msg, host)
        self._connected_addresses = [(ip, port) for ip, port in self._connected_addresses if ip != host]

    def disconnect_all(self, *args, **kwargs):
        # send disconnect message to every connected peer
        for peer in self._connected_addresses:
            msg = vp.encrypt(f"peer {self.sock_l_ip}:{self.sock_l_port} abort the connection").encode("utf-8")
            self.sock_c.sendto(msg, (peer[0], peer[1]))
        self._connected_addresses.clear()

    @property
    def connected_addresses(self):
        return self._connected_addresses
