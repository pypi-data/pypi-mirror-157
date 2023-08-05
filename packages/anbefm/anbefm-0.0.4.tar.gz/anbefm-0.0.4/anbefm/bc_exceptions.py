
class CommonException(Exception):
    def __init__(self, val: str):
        self._val = val

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self._val)


class NoModuleException(CommonException):
    def __init__(self, val: str):
        super().__init__()


class NoDataSourceException(CommonException):
    def __init__(self, val: str):
        super().__init__()


class UnavailableDataSourceTypeException(CommonException):
    def __init__(self, val: str):
        super().__init__()
