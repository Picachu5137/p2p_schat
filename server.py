import socket
import ssl


def listen(ip: str = "127.0.0.1", port: int = 2401):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))

    print(f"Listening connection at {ip}:{port}")

    members = {}

