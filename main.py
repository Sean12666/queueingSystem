import RPi.GPIO as GPIO
import time


class Infrared:
    def __init__(self, pin):
        self.pin = pin
        self.pre = self.cur = False
        GPIO.setup(pin, GPIO.IN)

    def detect(self):
        self.pre = self.cur
        self.cur = GPIO.input(self.pin)
        return not self.pre and self.cur


class QSys:
    def __init__(self, name, fpin, bpin):
        self.name = name
        self.front = Infrared(fpin)
        self.back = Infrared(bpin)
        self.size = 0
        self.out = 0
        self.pre = self.cur = time.perf_counter()
        self.time = 0

    def __lt__(self, other):
        return self.update() < other.update()

    def pop(self):
        if self.front.detect() and self.size > 0:
            self.size -= 1
            return True
        return False

    def push(self):
        if self.back.detect():
            self.size += 1
            return True
        return False

    def update(self):
        rate = 1
        self.push()
        if self.pop():
            self.out += 1
        if self.size > 0:
            self.cur = time.perf_counter()
            rate = self.out / (self.cur - self.pre) * 60
        else:
            self.pre += time.perf_counter() - self.cur
            self.cur = time.perf_counter()
        self.time = self.size / rate

    def get_name(self):
        return self.name

    def get_time(self):
        return self.time


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    ql = []
    with open("queues.txt", encoding="utf-8") as f:
        for ln in f.readlines():
            inp = ln.split()
            ql.append(QSys(inp[0], int(inp[1]), int(inp[2])))
    try:
        while True:
            for q in ql:
                q.update()
            mq = min(ql)
            print("{0} time: {1} min".format(mq.name, round(mq.get_time(), 4)))
    except KeyboardInterrupt:
        GPIO.cleanup()
