'''
 # @ Author: brifuture
 # @ Create Time: 2021-04-15 12:16
 # @ Modified by: brifuture
 # @ Modified time: 2021-06-11 12:01
 # @ Description: This File is created and the program is coded by BriFuture. (c) All rights reserved.
    Provides TCP/UDP socket Server and client
 '''

import json
import socket
import select
import traceback
import logging
logger = logging.getLogger("network")

__version__ = "0.2.2"

from .sock import EventHandler, SocketClient, UdpSocketClient
import sys

class BaseServer():
    """ One can easily extend the base server for Tcp/Udp connection
    """
    maxsize = 500000
    def __init__(self):
        self._recvList = []
        self._sendList = []
        self._exceptList = []
        self.running = False
        try:
            self.epoll = select.epoll(self.maxsize)
        except:
            pass
    
    def __del__(self):
        try:
            self.epoll.close()
        except: 
            pass

    def stop(self):
        self.running = False

    def registerRead(self, r):
        if r in self._recvList:
            logger.debug(f"Client Registered Twice {r}")
            return
        logger.debug(f"Client Registered {r}")
        self.epoll.register(r.fileno(), select.EPOLLIN)
        self._recvList.append(r)
        self._exceptList.append(r)


    def removeRead(self, r):
        if r not in self._recvList:
            logger.warning(f"Client Not Exits {r}")
            return
        self.epoll.unregister(r.fileno(), select.EPOLLIN)
        self._recvList.remove(r)
        self._exceptList.remove(r)

    def registerWrite(self, w):
        if w in self._sendList:
            return
        self.epoll.register(w.fileno(), select.EPOLLOUT)
        self._sendList.append(w)

    def removeWrite(self, w):
        if w not in self._sendList:
            return
        
        self.epoll.unregister(w.fileno(), select.EPOLLOUT)
        self._sendList.remove(w)

    def serve_forever(self):
        self.running = True
        while self.running:
            self.serve_once(0.1)

    def serve_once(self, timeout=0.001):
        if len(self._recvList) == 0:
            return
        events = self.epoll.poll(timeout)

        for fileno, event in events:
            if event & select.EPOLLIN:
                for r in self._recvList:
                    if fileno == r.fileno():
                        r.handle_receive()
            elif event & select.EPOLLOUT:
                for s in self._sendList:
                    if fileno == s.fileno():
                        s.handle_send()
            elif event & select.EPOLLHUP:
                self.epoll.unregister(fileno)
                for r in self._recvList:
                    if fileno == r.fileno():
                        r.handle_except()
        # self.checkClients() # upper level call it

class TcpSocketServer(EventHandler, BaseServer):
    """
    Args:
        ip address
        port
    """
    ClientClass = SocketClient
    def __init__(self, ip, port, maxconn = 50000):
        super().__init__()
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._clients = {}
        # key: address tuple, value SocketClient
        self.registerRead(self)
        
        self._clientAdded = None
        self._clientRemoved = None
        try:
            self._server.bind((ip, port))
            logger.info(f"[TSS] EServer Listening: {ip}:{port}")
        except Exception as e:
            logger.critical(f"[TS] Unable to listening {ip}:{port}")
            sys.exit(1)

        self._server.listen(maxconn)
        self._server.setblocking(False)
        self.maxconn = maxconn

    def setClientAddedCallback(self, p):
        """ callback """
        self._clientAdded = p

    def setClientRemovedCallback(self, p):
        """ callback """
        self._clientRemoved = p

    def fileno(self):
        return self._server.fileno()

    def __repr__(self) -> str:
        return f"<TSS {self.fileno()} c: {len(self._recvList)}>"

    def needs_receive(self):
        return True

    def serve_forever(self):
        self.running = True
        count = 0
        while self.running:
            self.serve_once(0.01)
            count += 1
            if count % 12000 == 0:
                self.checkClients()

    def shutdown(self):
        self.removeAll()
        self._server.close()

    def __del__(self):
        self.shutdown()

    def checkClients(self):
        clients = list(self._clients.values())
        for c in clients:
            if not c.is_valid():
                self.removeClient(c)
        # logger.debug(f"Check Clients {len(self._clients)}")

    def removeAll(self):
        clients = list(self._clients.values())
        for c in clients:
            c.shutdown()
            self.removeClient(c)

    def removeClient(self, client):
        """
        Args
            client: SocketClient
        """
        if client == self: return

        logger.info(f"[TS] Removing {client.address} {len(self._recvList)}")
        try:
            self.removeRead(client)
        except: pass
        
        if client.address in self._clients:
            try:
                self._clients.pop(client.address, None)
            except: pass
            
        if self._clientRemoved:
            try:
                self._clientRemoved(client)
            except Exception as e:
                logger.warning(f"[TS] remove callback failed {e}")
    
    def _addClient(self, sock, address):
        """添加一个 客户端 socket，不可手动添加
        """

        c = TcpSocketServer.ClientClass(sock, address, except_callback=self.removeClient)
        self._clients[address] = (c)
        self.registerRead(c)
        if self._clientAdded:
            self._clientAdded(c)

    def handle_receive(self):
        """接收到TCP连接
        """
        (sock, address) = self._server.accept()
        if len(self._clients) >= self.maxconn:
            # 超出最大连接数
            logger.warning("[TSS] Receive many conns")
            sock.close()
            return
        if address not in self._clients:
            self._addClient(sock, address)
            logger.debug(f'[TS] Accept From {address}, Clients Count: {len(self._clients)}')
        else:
            self._clients[address].sock = sock
            self._clients[address].address = address
            self._clients[address]._isValid = True

from datetime import datetime
import threading

class UdpSocketServer(BaseServer):
    """支持绑定到多个UDP端口上，使用 processor 进行回调

    Args:
        port udpsocket will bind into

    Callback:
        processor(msg: bytes, addr: tuple)

    Usage:

    ```py
    server = UdpSocketServer(bufferSize = 4096)
    
    server.createListener(10000, "server1")
    server.addProcessor(lambda x, y: print(x, y), name="server1")

    # send 
    server.sendto("server1", b"this is a test")
    server.broadcast(b"this is a broadcast")

    # in default loop
    server.serve_forever()

    # in custom loop
    while True:
        ## .. do other things
        server.serve_once()
        ## .. do other things
    ```

    """
    ClientClass = UdpSocketClient
    def __init__(self, **kwargs):
        super().__init__()
        self._listeners = {}
        self.bufferSize = kwargs.get("bufferSize", 1024)
        self._processors = {}

    @property
    def listeners(self):
        return self._listeners

    def addProcessor(self, processor, name="default"):
        if name not in self._processors:
            self._processors[name] = processor
            # logger.debug(f"[USS] add processor for {name}")
        else:
            logger.warning("[USS] dumplicated add processor.")

    def createListener(self, port, name="default", ip="127.0.0.1", processor = None):
        if name in self._listeners.keys():
            return

        assert port > 0 and port < 65535, "In valid Port"

        logger.info(f"[USS] Server Listening for '{name}': {ip}:{port}")
        listener = self.ClientClass(port, ip, bufferSize=self.bufferSize, name=name)
        listener.parser = self.recvfrom
        listener.except_callback = self.handle_except

        self._listeners[name] = listener
        self.registerRead(listener)
        if processor is not None:
            self.addProcessor(processor, name)
        # self._sendList.append(listener)
        return listener
    
    def handle_except(self, client):
        logger.warning(f"[USS] Listener quit, {client.name}")
        try:
            self._listeners.pop(client.name)
            self.removeRead(client)
        except:
            pass

    def send(self, msg: bytes, name = "default"):
        """send msg to server by
        """
        if name not in self._listeners:
            return
        self._listeners[name].send(msg)

    def sendto(self, msg: bytes, peer, name="default"):
        if name not in self._listeners:
            return
        self._listeners[name].sock.sendto(msg, peer)

    def broadcast(self, msg):
        for c in self._listeners.values():
            c.send(msg)

    def recvfrom(self, byteAddrPair, name):
        """recv data from one udp server
        """
        if name in self._processors:
            # process will executed
            process = self._processors[name]
            message = byteAddrPair[0]
            address = byteAddrPair[1]
            process(message, address)
        # else:
        #     logger.debug(f"No processor for{name}, {byteAddrPair}")
