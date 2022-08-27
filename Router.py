import socket
import time


class Router:

    router_size: int = None
    router_state: bytearray = None
    router_ip: str = None
    router_port: int = None
    connection: socket.socket = None
    router_size: int = 128  # TODO: Determine this from the router

    def __init__(self, ip_address: str = "192.168.4.20", port: int = 9990):
        self.router_ip = ip_address
        self.router_port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.connection.connect((self.router_ip, self.router_port))

    def disconnect(self):
        self.connection.close()

    def write_state(self, router_state: bytearray):
        # TODO: arrange sleep timings, perhaps we don't need so much delay
        self.connect()

        # TODO: does this achieve anything?
        self.connection.send(("VIDEO OUTPUT ROUTING:\n").encode("cp1250"))
        for i in range(self.router_size):
            self.connection.send(
                (str(i) + " " + str(router_state[i]) + "\n").encode("cp1250"))
        self.connection.send("\n".encode("cp1250"))
        self.disconnect()

        self.router_state = router_state  # TODO: Determine this from the router

    def read_state(self):
        self.connect()
        data = self.connection.recv(8888)
        self.disconnect()
        # read and decode from router
        data = data.decode("cp1250")
        data = data.split('\n')
        print(data)
        print("\n")

        s = next(i for i in data if i.startswith("Video outputs:"))
        print(s)
        s = s.split(":")
        self.router_size = int(s[1])
        # print(f"[{time.ctime()}] Router size read: ")
        print(self.router_size)

        # send command to read output routing
        self.connection.send(b"video output routing:\n\n")
        time.sleep(0.1)
        # read and decode from router
        outrouting = self.connection.recv(4096)
        outrouting = outrouting.decode("cp1250")
        outrouting = outrouting.split('\n')
        # delete first three rows
        for i in range(3):
            a = outrouting.pop(0)
        print("\n----- OUTROUTING O<I CLEAN (3 first rows removed, zero-based): -----")
        print(outrouting)

        self.router_state = bytearray(self.router_size)

        for i in range(self.router_size):
            splitted = outrouting[i].split(' ')
            self.router_state[int(splitted[0])] = int(splitted[1])

        return self.router_state

    def __del__(self):
        if self.connection:
            try:
                self.connection.close()
            except:
                print(
                    f"Connection to router at {self.router_ip}:{self.router_port} already closed")
