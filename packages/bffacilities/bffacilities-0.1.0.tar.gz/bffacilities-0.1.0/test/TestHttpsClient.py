import unittest
from bffacilities.network import TcpSocketServer, SocketClient, logger
from bffacilities.utils import changeLoggerLevel
import logging
changeLoggerLevel(logger, logging.DEBUG)
import time
import threading
import asyncio
import urllib.request

async def createClient(id, address, to):
    # client = SocketClient.createTcpClient(address)
    keyword = "python"

    url = f"https://{address[0]}:{address[1]}/"
    try:
        i = 0
        while i < 50:
            resp = urllib.request.urlopen(url, timeout=2)
            if resp.getcode() == 408:
                print(id, "-- timeout")
            else:
                data = resp.read().decode("utf-8")
                # print(id, "--", i, data)
            # client.sock.send(data.encode())
            await asyncio.sleep(to) 
            i += 1
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        print("Clinet occure error:", e)
    print("Client Done ", id)
async def main(args):
    tasks = []
    for i in range(args["count"]):
        c = createClient(i, (args["host"], args["port"]), args["timeout"])
        tasks.append(c)
    print("***start**")
    try:
        await asyncio.gather(*tasks)
    except (KeyboardInterrupt, SystemExit):
        # asyncio.
        pass
    

if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser("TestTcpSocketClient")
    parser.add_argument("--port", type=int, default=54134, help="set port")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="set host")
    parser.add_argument("--count", type=int, default=10, help="parallel count")
    parser.add_argument("--timeout", type=int, default=10, help="parallel count")
    args = vars(parser.parse_args(sys.argv[1:]))
    
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(args))

