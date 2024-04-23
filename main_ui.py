from PyQt6 import QtWidgets, uic
import sys
import threading
import re
import client_udp


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("p2psm.ui", self)

        ip, ip_pressed = QtWidgets.QInputDialog.getText(self, "configuration", "enter host ip(default is 127.0.0.1)")

        if not ip_pressed or not re.match(r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}", ip):
            ip = "127.0.0.1"

        port, port_pressed = QtWidgets.QInputDialog.getInt(self, "configuration", "enter host port(default is 2424)")

        if not port_pressed or (port < 1070 or 65535 < port):
            port = 2424

        self.client = client_udp.Client(ip=ip, port=port)
        print(f"client socket for connections binded on {self.client.sock_l_ip}:{self.client.sock_l_port} ")

        self.listen_thread = threading.Thread(target=self.listen_thread,
                                              name="listen thread", daemon=True)
        self.listen_thread.start()
        print(f"successfully start {self.listen_thread.name}")
        print(f"{threading.active_count()}")

        # btn_refresh
        self.btn_refresh = self.findChild(QtWidgets.QToolButton, "btn_refresh")
        self.btn_refresh.clicked.connect(self.refresh_connections)

        # btn_connect
        self.btn_connect = self.findChild(QtWidgets.QToolButton, "btn_connect")
        self.btn_connect.clicked.connect(self.peer_connect)

        # btn_disconnect
        self.btn_disconnect = self.findChild(QtWidgets.QToolButton, "btn_disconnect")
        self.btn_disconnect.clicked.connect(self.peer_disconnect)

        # btn_disconnect_all
        self.btn_disconnect_all = self.findChild(QtWidgets.QToolButton, "btn_disconnect_all")
        self.btn_disconnect_all.clicked.connect(self.peer_disconnect_all)

        # btn_info
        self.btn_info = self.findChild(QtWidgets.QToolButton, "btn_info")
        self.btn_info.clicked.connect(self.show_info)

        # btn_msg_send
        self.btn_msg_send = self.findChild(QtWidgets.QToolButton, "btn_msg_send")
        self.btn_msg_send.clicked.connect(self.send_msg)

        # connections
        self.connections = self.findChild(QtWidgets.QListWidget, "connections")

        # messages
        self.messages = self.findChild(QtWidgets.QListWidget, "messages")

        # msg_box
        self.msg_box = self.findChild(QtWidgets.QTextEdit, "msg_box")

    def listen_thread(self):
        while True:
            recv_packet = self.client.listen()
            if recv_packet:
                msg, addr = recv_packet
                peer_name = self.client.get_peer_by_addr(addr)[2]
                item = QtWidgets.QListWidgetItem()
                item.setText(f"{peer_name} to You:\n{msg}\n")
                self.messages.addItem(item)

    def peer_connect(self):
        peer_name, pressed_name = QtWidgets.QInputDialog.getText(self, "new connection", "enter peer name")
        peer_addr, pressed_addr = QtWidgets.QInputDialog.getText(self, "new connection", "enter peer ip")
        peer_port, pressed_port = QtWidgets.QInputDialog.getInt(self, "new connection", "enter peer port")
        if pressed_name and pressed_addr and pressed_port:
            if peer_name:
                if re.match(r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}", peer_addr) and (
                        1023 < peer_port < 65535):
                    self.client.connect(peer_name, peer_addr, peer_port)
                else:
                    print("invalid input")
            self.refresh_connections()

    def peer_disconnect(self):
        if not (current_peer := self.connections.currentItem()):
            print("there is no selected peer")
        else:
            peer = current_peer.text()
            self.client.disconnect(peer_name=peer)
        self.refresh_connections()

    def peer_disconnect_all(self):
        self.client.disconnect_all()
        self.refresh_connections()

    def send_msg(self):
        msg = self.msg_box.toPlainText()
        if not (current_peer := self.connections.currentItem()):
            print("there is no selected peer")
        else:
            current_peer_name = current_peer.text()
            self.client.send_msg(msg, current_peer_name)
            item = QtWidgets.QListWidgetItem()
            item.setText(f"You to {current_peer_name}:\n{msg}\n")
            self.messages.addItem(item)
            self.msg_box.clear()

    def refresh_connections(self):
        connections = [f"{i[2]}" for i in self.client.connected_addresses]
        self.connections.clear()
        self.connections.addItems(connections)

    def show_info(self):
        info_text = """
        p2p мессенджер с поддержкой шифрования сообщений
        был разработан в качестве обучающего проекта
        """
        info_box = QtWidgets.QMessageBox()
        info_box.setText(info_text)
        info_box.setWindowTitle("info")
        info_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)
        info_box.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
