import select
from bffacilities.utils import createLogger
logger = createLogger('network', savefile=False, stream=True, timeformat="%H:%M:%S")
import socket
from .sock import  SocketClient, UdpSocketClient, EventHandler
if hasattr(select, "epoll"):
    from .servers import BaseServer, TcpSocketServer, UdpSocketServer
else:
    from .socketserver_select import  BaseServer, TcpSocketServer, UdpSocketServer