day = 24 * 60 * 60

class UptimeEstimator:

    def __init__(self):
        self.v = []

    def add(self, time, isup):
        assert time.tzinfo is None
        self.v.append([(time.hour * 60 + time.minute) * 60 + time.second + time.microsecond / 1e6, isup])

    def uptime(self):
        v = sorted(self.v)
        first = v[0][0]
        last = v[-1][0]
        v.insert(0, [last - day, None])
        v.append([first + day, None])
        acc = 0
        for w, x, y in zip(v[:-2], v[1:-1], v[2:]):
            if x[1]:
                acc += y[0] - w[0]
        return acc / day * 50
