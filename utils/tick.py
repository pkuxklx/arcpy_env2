import time

class Timer():
    def __init__(self, n = 3):
        self.t1 = [time.time()] * n
        self.t2 = [0] * n
        self.n = n

    def tk(self, k = 0):
        self.t2[k] = time.time()
        print("Run time: %.2fs" %(self.t2[k] - self.t1[k]))
        self.t1[k] = self.t2[k]

if __name__ == '__main__':
    ti = Timer()
    for i in range(2000):
        for j in range(2000):
            pass
    ti.tk(k = 0)
    for i in range(5000):
        for j in range(5000):
            pass
    ti.tk(k = 0)
    ti.tk(k = 1)