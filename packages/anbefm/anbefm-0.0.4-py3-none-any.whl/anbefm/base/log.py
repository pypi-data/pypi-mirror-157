class Log():
    def __init__(self):
        pass

    def print(self, *args, **kvargs):
        print(*args, flush=True, **kvargs)
