

class Method:

    def __init__(self):
        self.smart = None
        self.logic = None

    def register(self, mode: str):
        
        def decorator(func):
            if mode == "smart":
                self.smart = func
            elif mode == "logic":
                self.logic = func
            else:
                raise ValueError(f"{mode} is not a valid keyword")
        return decorator

    def __call__(self, *args, **kwargs):
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

