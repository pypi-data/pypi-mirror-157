
from _c import Method


def smart_method(func):
    _m = Method()
    return _m



class Test:

    @smart_method
    def test(a, b):
        pass

    @test.register("smart")
    def test_smart(a, b):
        print(a / b, "smart")

    @test.register("logic")
    def test_logic(a, b):
        print(a + b, "logic")


if __name__ == "__main__":
    t = Test()
    t.test(1, 2)
    t.test(1, 0)

