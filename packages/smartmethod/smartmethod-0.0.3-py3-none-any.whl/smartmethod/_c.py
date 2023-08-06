from types import FunctionType


SUPPORTED_MODES = ["smart", "logic"]

class BoundMethod:
    def __init__(self):
        self.smart = None
        self.logic = None
        self.ref = None
        self.static = False

    def register(self, mode: str):
        """ register smart and logic functions """
        self._validate_mode(mode)
        def decorator(obj):
            if isinstance(obj, (staticmethod, classmethod)):
                self._register_cls(obj, mode)
            if type(obj) is FunctionType:
                self._register_func(obj, mode)
        return decorator

    def _validate_mode(self, mode: str):
        if type(mode) is not str:
            raise TypeError("Mode must be of type 'str'")
        if mode not in SUPPORTED_MODES:
            raise ValueError(f"{mode} is currently not supported")

    def _register_cls(self, cls, mode):
        setattr(self, mode, cls.__func__)
        if isinstance(cls, staticmethod):
            self.static = True

    def _register_func(self, func, mode):
        setattr(self, mode, func)

    def _call(self, *args, **kwargs):
        if self.smart and self.logic:
            try:
                return self.smart(*args, **kwargs)
            except Exception as e:
                return self.logic(*args, **kwargs)
            finally:
                pass
        elif self.logic:
            return self.logic(*args, **kwargs)
        else:
            raise NotImplementedError("You need a pure logical method to ensure accessibility!")

    def __get__(self, instance, cls):
        self.ref = instance or cls
        return self

    def __call__(self, *args, **kwargs):
        if not self.static:
            self._call(self.ref, *args, **kwargs)
        else:
            self._call(*args, **kwargs)

