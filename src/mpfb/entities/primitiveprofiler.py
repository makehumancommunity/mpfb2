import time

_registered_profilers = dict()

class _PrimitiveProfiler:

    def __init__(self):
        self.entered = dict()
        self.completed = dict()

    def enter(self, location):
        if location in self.entered:
            print(location + " fanns redan!")
        self.entered[location] = time.time()

    def leave(self, location):
        if not location in self.entered:
            print(location + " fanns inte!")
            return
        if not location in self.completed:
            self.completed[location] = []
        self.completed[location].append(time.time() - self.entered[location])
        del self.entered[location]

    def dump(self):
        for name in self.completed:
            out = "  " + name.ljust(60)
            out = out + str("count=" + str(len(self.completed[name]))).ljust(20)
            total = 0.0
            max = 0.0
            min = 40000.0
            for completed in self.completed[name]:
                total = total + completed
                if completed < min:
                    min = completed
                if completed > max:
                    max = completed
            out = out + str("total=" + str(round(total,4))).ljust(15)
            out = out + str("min=" + str(round(min,4))).ljust(15)
            out = out + str("max=" + str(round(max,4))).ljust(15)
            out = out + str("avg=" + str(round(total / len(self.completed[name]),4))).ljust(15)
            print(out)

def PrimitiveProfiler(name):
    global _registered_profilers
    if not name in _registered_profilers:
        _registered_profilers[name] = _PrimitiveProfiler()
    return _registered_profilers[name]
