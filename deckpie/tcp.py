import socket


class TcpClient(object):
    receive_buffer = 50
    __connected = False
    port = None

    def __init__(self, params):
        self.__initialized = False
        if "url" in params:
            self.target = socket.gethostbyname(params['url'])
        else:
            self.target = params['ip']
        self.source = socket.gethostbyname(socket.gethostname())
        self.port_id = params['port'] if 'port' in params else 32

    def __enter__(self):
        print('Initializing Network...')
        self.port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__initialized = True
        self.port.bind((self.source, self.port_id))

    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb
        if self.__initialized:
            self.port.close()

    def connect(self):
        self.port.connect((self.target, self.port_id))
        self.__connected = True

    def sendall(self, string):
        if not self.__connected:
            raise IOError("Network Error", "tcp socket not connected")
        self.port.sendall(string)

    def receive(self, time_out=None):
        """receive everything as bytearray till receives nothing"""
        if not self.__connected:
            raise IOError("Network Error", "tcp socket not connected")
        old_time_out = self.port.gettimeout()
        if time_out:
            self.port.settimeout(time_out)
        result = []
        while True:
            temp = self.port.recv(self.receive_buffer)
            if temp == b'':
                break
            else:
                result.append(temp)
        self.port.settimeout(old_time_out)
        return b''.join(result)


class TcpServer(TcpClient):
    max_time_out = 60
    connection_limit = 2
    port = None
    __connected = False
    listener = None

    def __enter__(self):
        print('Initializing Network...')
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__initialized = True
        self.listener.bind((self.source, self.port_id))

    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb
        if self.__initialized:
            self.listener.close()
        if self.__connected:
            self.port.close()

    def connect(self):
        self.listener.listen(self.connection_limit)
        old_time_out = self.port.gettimeout()
        self.listener.settimeout(self.max_time_out)
        self.port, _ = self.listener.accept()
        self.listener.settimeout(old_time_out)
        self.__connected = True
