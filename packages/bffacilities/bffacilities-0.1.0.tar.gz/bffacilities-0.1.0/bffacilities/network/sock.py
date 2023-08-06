"""
Base Sock
"""
from multiprocessing.sharedctypes import Value
import socket
import logging
import traceback

__version__ = "0.1.1"

logger = logging.getLogger("network")
class EventHandler:
    def fileno(self):
        """Return the associated file descriptor"""
        raise ValueError('Not Implemented must implement')

    def handle_receive(self):
        'Perform the receive operation'
        pass

    def handle_send(self):
        'Send outgoing data'
        pass

    def handle_except(self):
        pass

    def is_valid(self):
        return True

class SocketClient(EventHandler):
    """
    1. 通过继承该类进行客户端编写，
    2. 通过 parser 回调函数进行消息读取

    Args:
        sock: socket
        address: client socket address recved from server,
            useful when other want to communicate or 
            identify the client

        except_callback: function(client: SocketClient)
    """
    def __init__(self, sock, address, **kwargs):
        self._sock = sock
        self._sock.setblocking(False)
        if address is None:
            try:
                self.address = self._sock.getsockname()
            except: 
                self.address = None
        else:
            self.address = address

        self._isValid = True

        self._parse = None
        self._server = None
        self.except_callback = kwargs.get("except_callback", None)
        self.bufferSize = kwargs.get("bufferSize", 2048)

    @staticmethod
    def createTcpClient(serverAddr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc = SocketClient(sock, None)
        sc._sock.setblocking(True)
        sc._server = serverAddr
        return sc

    @property
    def sock(self):
        return self._sock

    def connect(self):
        if self._server is None:
            return
        try:
            self._sock.connect(self._server)
            if self.address is None:
                self.address = self._sock.getsockname()
        except:
            logger.warning(f"[SC] Error connecting {self._server} [{self.address}]")
            self.handle_except()
        finally:
            pass

    def shutdown(self):
        self._sock.close()

    def __del__(self):
        self._sock.close()

    @property
    def parser(self):
        return self._parse

    @parser.setter
    def parser(self, parse):
        """传入一个解析器即可
        @deprecated use setParser
        ```py
        # data is a dict
        def parse(data, socketClient): print(data, socketClient)

        client.parser = parse
        ```
        """
        raise ValueError("Unsupported action, use setParser Instead")
        try:
            self._parse = parse
            # parse('""', self) # pass empty string
        except Exception as e:
            logger.critical(f"[TC] ***** Error testing parser: {e} ****")

    def setParser(self, parser, testJson=True):
        """传入解析器，若协议为 json，则进行测试
        """
        if testJson:
            try:
                parser('""', self) # pass empty string
                self._parse = parser
            except:
                logger.critical(f"[TC] ***** Error testing parser, it will be ignored ****")
        else:
            self._parse = parser

    def is_valid(self):
        return self._isValid

    def fileno(self):
        return self._sock.fileno()

    def __repr__(self):
        return f'<Socket Client, {self._sock.fileno()}, {self.address}>'

    def handle_receive(self):
        """Handle receive data, default processor
        subclass could replace this methods to receive binary data
        """
        msg = None
        try:
            msg = self._sock.recv(self.bufferSize)
            if not msg:
                self.handle_except()
                return
        except socket.error:
            self.handle_except()
        except Exception as e:
            logger.warning(f"[TC] recv {e}")
        
        if msg is None: return

        if self._parse:
            try:
                self._parse(msg.decode(), self)
            except Exception as e:
                logger.warning(f"[TC] parse {msg}, {e}")
                traceback.print_exc()
        else:
            logger.debug(msg)

    def handle_send(self):
        pass

    def handle_except(self):
        """注意不要在 callback 中重新创建 client，否则函数调用堆栈将会溢出
        """
        self._sock.close()
        self._isValid = False
        if self.except_callback:
            self.except_callback(self)


class UdpSocketClient(EventHandler):
    def __init__(self, port, ip = "127.0.0.1", name="default", **kwargs):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (ip, port)
        self.sock.settimeout(0)
        self.sock.setblocking(False)
        self.sock.bind(self.address)
        self.bufferSize = kwargs.get("bufferSize", 1024)
        self.name = name
        self._isValid = True
        self._parse = None
        self._peer = None
        self._peers = []

        self.except_callback = kwargs.get("except_callback", None)
        # self.keepFirstPeer = False # if true, the first peer will always be used

    @property
    def parser(self):
        return self._parse

    @parser.setter
    def parser(self, parse):
        """传入一个解析器即可
        ```
        def parse(data, recver): 
            print(data, "From", recver)

        client.parser = parse
        ```
        """
        self._parse = parse

    def send(self, msg):
        """
        Args
            msg bytes
        """
        for p in self._peers:
            self.sock.sendto(msg, p)

    def is_valid(self):
        return self._isValid

    def fileno(self):
        return self.sock.fileno()

    def __repr__(self):
        return f"<UdpSocketClient {self.name} {self.address} {self.bufferSize} {self.sock.fileno()}>"

    def handle_receive(self):
        """Handle receive data, default processor
        subclass could replace this methods to receive binary data
        """
        bytesAddressPair = None
        try:
            bytesAddressPair = self.sock.recvfrom(self.bufferSize)
        except Exception as e: 
            # logger.warning(f"[UC] {self}  recv error : {e}")
            # traceback.print_exc()
            # ICMP recved cause the error, ignore it
            pass

        # message = bytesAddressPair[0]
        if not bytesAddressPair:
            # self.handle_except()
            return
        if not bytesAddressPair[1] in self._peers:
            logger.info(f"[UC] new client added: {bytesAddressPair[1]}")
            self._peers.append(bytesAddressPair[1])
        if self._parse:
            try: 
                self._parse(bytesAddressPair, self.name)
            except Exception as e:
                logger.warning(f"[UC] parse error: {e}")
                traceback.print_exc()

    def handle_send(self):
        pass

    def handle_except(self):
        self.sock.close()
        self._isValid = False
        if self.except_callback:
            self.except_callback(self)

