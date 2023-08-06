import unittest
from bffacilities.network import TcpSocketServer, SocketClient, logger
from bffacilities.utils import changeLoggerLevel
import logging
changeLoggerLevel(logger, logging.DEBUG)
import time
import threading
import asyncio

__version__ = "0.0.10"

async def createClient(id, address, waitCount):
    client = SocketClient.createTcpClient(address)
    def parse(x, c):
        print(f"{client} , {x}")
    client.setParser(parse, testJson=False)
    try:
        client.connect()
        data = f"{{'name': '{id}'}}"
        i = 0
        while i < waitCount:
            client.sock.send(data.encode())
            await asyncio.sleep(1) 
            # client.handle_receive()
            i += 1
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        print("Client exception:", e)
    client.sock.close()
    print("Client Done ", id)
async def main(args):
    tasks = []
    for i in range(args["count"]):
        tasks.append(createClient(i, (args["host"], args["port"]), args["wait"]))
    print("start")
    try:
        await asyncio.gather(*tasks)
    except (KeyboardInterrupt, SystemExit):
        pass
    

if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser("TestTcpSocketClient")
    parser.add_argument("--port", type=int, default=54134, help="set port")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="set host")
    parser.add_argument("--count", type=int, default=10, help="parallel count")
    parser.add_argument("--wait", type=int, default=10, help="parallel count")
    args = vars(parser.parse_args(sys.argv[1:]))
    
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(args))

