class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwds):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwds)
            cls._instances[cls] = instance

        return cls._instances[cls]


class Singleton_meta(metaclass=SingletonMeta):
    def print_log(self):
        print("I did something")
        pass


class Singleton_new:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def print_log(self):
        print("I did something")
        pass


class _Singolton_import:
    def print_log(self):
        print("I did something")
        pass


isinstance = _Singolton_import()
