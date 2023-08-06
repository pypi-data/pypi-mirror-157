import random
class A(object):
    def __init__(self, id=None) -> None:
        super().__init__()
        if id is None:
            id = random.randint(0, 1000000)
        self.id = id
    
    def quit(self):
        print(f"A [{self.id} is quiting]")

    def __repr__(self) -> str:
        return f"A [{self.id}]"

from threading import Thread
import threading
from queue import Queue

class Mgr(object):
    def __init__(self) -> None:
        super().__init__()
        self._items = {}
        self.q = Queue(1000)

    def __enter__(self):
        id = threading.get_ident()
        a = A(id)
        self._items[id] = a
        self.q.put(a)
        print("enter ", id, "size", len(self._items))
        return a

    def __exit__(self, exc_type, exc_val, exc_tb):
        id = threading.get_ident()
        print("Done Before", self._items)
        a = self._items.pop(id)
        s = random.randint(3, 10)
        out = self.q.get()
        sleep(s)
        if a is not None:
            a.quit()
        print("Done ", s, out)
        sleep(s)


from time import sleep
# from threading.pool import Pool
def test(mgr):
    sleep(random.random() + 0.1)
    with mgr as m:
        print("Currently using ", m.id)
        sleep(3)
    pass
if __name__ == "__main__":
    mgr = Mgr()
    threads = []
    for i in range(5):
        t = Thread(target=test, args=(mgr, ))
        t.start()
        threads.append(t)
    # print("====================\n\n")
    for i in threads:
        i.join()
