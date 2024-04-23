import socket
import ssl
import random
import vp
import pickle
from typing import NamedTuple


class Packet(NamedTuple):
    packet_type: str
    payload: str
    port: int


class Client:
    # maximum udp packet size without data loss = 576
    UDP_MAX_SIZE = 4096

    def __init__(self, ip: str = socket.gethostbyname(socket.gethostname()), port: int = 2424):
        self.private_key, self.public_key = vp.generate_keys()

        self.sock_l_port = port
        self.sock_l_ip = ip
        self.sock_l = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_l.bind((ip, port))

        self.sock_c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._connected_addresses = []

    def listen(self) -> tuple[str, tuple[str, int]] | None:
        encoded_data, addr = self.sock_l.recvfrom(Client.UDP_MAX_SIZE)
        decoded_data: Packet = pickle.loads(encoded_data)
        # addr = (ip, port)
        addr = (addr[0], decoded_data.port)

        # decoded_data = (packet_type: str, data: , port: int)
        if any(addr[0] == peer[0] and addr[1] == peer[1] for peer in self._connected_addresses):
            # TODO: сделать обработку пакетов ["MESSAGE", msg, port]

            # message processing
            # decoded_data = ["MESSAGE", encrypted_msg, port: int]
            if decoded_data.packet_type == "MESSAGE":
                encrypted_msg = decoded_data.payload
                decrypted_msg = vp.decrypt(encrypted_msg)
                return decrypted_msg, addr

            # TODO: сделать механизм подключения и обмена ключами,
            #  только надо придумать протокол шифрования и подключения двух узлов
            # processing peer connection
            if decoded_data[0] == "CONNECTION":
                pass

    def package_process(self, encoded_data: bytes | bytearray, addr: tuple[str, int]):
        decoded_data: Packet = pickle.loads(encoded_data)
        addr = (addr[0], decoded_data.port)

        if any(addr[0] == peer[0] and addr[1] == peer[1] for peer in self._connected_addresses):
            if decoded_data.packet_type == "MESSAGE":
                encrypted_msg = decoded_data.payload
                decrypted_msg = vp.decrypt(encrypted_msg)
                return decrypted_msg, addr

            # TODO: сделать механизм подключения и обмена ключами,
            #  только надо придумать протокол шифрования и подключения двух узлов
            # processing peer connection
            if decoded_data[0] == "CONNECTION":
                pass

    def connect(self, name: str, ip: str = "127.0.0.1", port: int = 2424):
        """
        add new peer to connected addresses
        :param name: name of peer using for identify peer
        :param ip: ip of peer
        :param port: port of peer
        """
        new_peer = [ip, port, name, "pubkey"]  # instead pubkey must be ciphering pubkey
        if any([name == peer[2] for peer in self._connected_addresses]):
            print(f"name {name} already connected")
        elif any([(ip == peer[0] and port == peer[1]) for peer in self._connected_addresses]):
            print(f"{ip}:{port} already connected")
        else:
            self._connected_addresses.append(new_peer)
            print(f"connected {ip}:{port} as {name}")

    def send_msg(self, msg: str, peer_name: str):
        """
        send msg to peer with peer_name
        :param msg: message to send
        :param peer_name: name of peer
        :return None:
        """
        # msg = ["MESSAGE", msg, id: tuple = (ip, port)]
        peer = self.get_peer_by_name(peer_name)
        if peer:
            peer_addr = tuple(peer[:2])
            packet = Packet(packet_type="MESSAGE", payload=vp.encrypt(msg), port=self.sock_l_port)
            encrypted_msg = pickle.dumps(packet)
            self.sock_c.sendto(encrypted_msg, peer_addr)
        else:
            print("no such peer")

    def disconnect(self, peer_name: str):
        """
        removes a peer with a peer_name from the connected addresses
        :param peer_name: name of peer to disconnect
        :return:
        """
        self._connected_addresses = [peer for peer in self._connected_addresses if peer[2] != peer_name]

    def disconnect_all(self):
        """
        disconnect all peers
        :return:
        """
        self._connected_addresses.clear()

    def get_peer_by_name(self, peer_name: str, *args, **kwargs) -> tuple | None:
        """
        returns the first peer with the specified peer_name, else None
        :param peer_name: name of peer for search
        :return:
        """
        for peer in self._connected_addresses:
            if peer[2] == peer_name:
                return peer

    def get_peer_by_addr(self, addr: tuple) -> tuple | None:
        """
        return the first peer with the specified ip, else None
        :param addr: (ip: str, port: int)
        :return:
        """
        ip, port = addr
        for peer in self._connected_addresses:
            if peer[0] == ip and peer[1] == port:
                return peer

    @property
    def connected_addresses(self) -> list:
        return self._connected_addresses
