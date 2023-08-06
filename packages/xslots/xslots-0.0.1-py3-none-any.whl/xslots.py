class Slots:
    def __init__(self, amount, mn, mx, start_value):
        self.mn = mn
        self.mx = mx
        self.start = start_value
        self.slots = [start_value for _ in range(amount)]
    
    def __str__(self):
        slots = map(str, self.slots)
        return "".join(slots)
    
    def increase(self, idx = 0):
        if len(self.slots) <= idx:
            self.slots.append(self.start)
        else:
            if self.slots[idx] == self.mx:
                self.slots[idx] = self.mn
                self.increase(idx + 1)
            else:
                self.slots[idx] += 1
