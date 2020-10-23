from multiprocessing.managers import BaseManager
from multiprocessing import Process
import time
class MathsClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def add(self, x, y):
        return x + y
    def mul(self, x, y):
        return x * y
    def test(self):
        self.aaa = 500
    def get(self):
        print(self.a)
        print(self.b)
    def change(self, a,b):
        self.a = a
        self.b = b
    def prin(self):
        while True:
            print(self.a, self.b)
class MyManager(BaseManager):
    pass

MyManager.register('Maths', MathsClass)

if __name__ == '__main__':
    with MyManager() as manager:

        maths = manager.Maths(777,888)
        p1 = Process(target=maths.prin)
        p1.start()
        time.sleep(1)
        maths.change(111111,222222)
        p1.join()
        # p2 = Process(target=maths.prin)
        # p2.start()
        # maths.change(111111,222222)