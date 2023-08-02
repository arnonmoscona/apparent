#  Copyright (c) Arnon Moscona 2023. under Apache2 license

from apparent.timing import Timer


class CustomTimerRegistry:
    """Used to test @timed using someting other than the default registry"""
    def __init__(self):
        self.reg: dict[str, Timer] = {}

    def get(self, name: str) -> Timer:
        if name not in self.reg:
            self.reg[name] = Timer(name)
        return self.reg[name]

    def clear(self):
        self.reg.clear()

    def names(self):
        return list(self.reg.keys())

    def timers(self):
        return list(self.reg.values())

    def reset(self, name: str):
        if name in self.reg:
            del self.reg[name]
