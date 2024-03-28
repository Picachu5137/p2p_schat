import client_udp
import argparse
import threading

parser = argparse.ArgumentParser()
parser.add_argument("-hP", "--host-port", default=2424, type=int, required=False)
parser.add_argument("-ip", default="127.0.0.1", type=str, required=False)

args = parser.parse_args()
host_port = args.host_port
host_ip = args.ip


def listen_thread(cli: client_udp.Client):
    while True:
        msg, addr = cli.listen()
        print(msg)


cli1 = client_udp.Client(host_ip, host_port)


def connect(cli: client_udp.Client, host, port, *args, **kwargs):
    cli.connect(host, port)


def disconnect(cli: client_udp.Client, host, *args, **kwargs):
    cli.disconnect(host)


def disconnect_all(cli: client_udp.Client, *args, **kwargs):
    msg = cli.disconnect_all()
    print(msg)


COMMANDS = (
        "/connect",
        "/disconnect",
        "/disconnect_all"
        )

lt = threading.Thread(target=listen_thread, args=(cli1,))
lt.start()


def start():
    while True:
        msg = input("you: ")

        if (msg := msg.split())[0] in COMMANDS:
            if msg[0] == "/connect":
                cli1.connect(msg[1], int(msg[2]))
            elif msg[0] == "/disconnect":
                cli1.disconnect(msg[1])
            elif msg[0] == "/disconnect_all":
                cli1.disconnect_all()

        else:
            cli1.send_msg("".join(msg[:-2]), msg[-2], int(msg[-1]))


if __name__ == "__main__":
    print("chat start")
    start()
