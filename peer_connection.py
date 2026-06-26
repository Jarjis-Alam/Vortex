import socket


class PeerConnection:

    def __init__(
        self,
        ip,
        port
    ):

        self.ip = ip
        self.port = port

    def connect(self):

        try:

            self.sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            # 5s connection timeout
            self.sock.settimeout(5)

            self.sock.connect(
                (
                    self.ip,
                    self.port
                )
            )

            # After connecting, set longer
            # timeout for data transfer
            self.sock.settimeout(30)

            # 4 MB socket buffers
            self.sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_RCVBUF,
                4 * 1024 * 1024
            )

            self.sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_SNDBUF,
                4 * 1024 * 1024
            )

            self.sock.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_NODELAY,
                1
            )

            print("Connected!")

            return True

        except Exception as e:

            print(e)

            return False