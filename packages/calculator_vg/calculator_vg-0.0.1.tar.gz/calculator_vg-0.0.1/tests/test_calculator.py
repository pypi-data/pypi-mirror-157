import py.test
from calculator import calculator as c
from hypothesis import given, assume, strategies as st


def test_initial_values():
    calc = c.Calculator()
    assert calc.result == 0


def test_method__reset__basic():
    calc = c.Calculator()
    calc.reset()
    assert calc.result == 0

    calc.reset(to=100)
    assert calc.result == 100


def test_method__reset__wrong_inputs():
    calc = c.Calculator()
    with py.test.raises(TypeError):
        calc.reset("a")

    with py.test.raises(TypeError):
        calc.reset(["a"])

    with py.test.raises(TypeError):
        calc.reset([1])

    with py.test.raises(TypeError):
        calc.reset(1, 2)


def test_method__take_n_root__basic():
    calc = c.Calculator()

    calc.reset(to=1000)
    calc.take_n_root(3)
    assert round(calc.result, 5) == 10

    calc.reset(to=1000)
    calc.take_n_root(-3)
    assert round(calc.result, 5) == 0.1

    with py.test.raises(ZeroDivisionError):
        calc.take_n_root(0)


@given(
    base=st.floats(min_value=-10000, max_value=10000),
    n=st.floats(min_value=-10000, max_value=10000),
)
def test_method__take_n_root__extended(base, n):
    assume(abs(base) >= 0.0001)
    assume(abs(n) >= 0.0001)

    calc = c.Calculator()
    calc.reset(to=base)

    if (n == 0) or (base == 0 and n < 0):
        with py.test.raises(ZeroDivisionError):
            calc.take_n_root(n)

    elif base == 0 and n > 0:
        calc.take_n_root(n)
        assert calc.result == 0

    elif base != 0 and n != 0:
        calc.take_n_root(n)
        assert calc.result == (base ** (1 / n))

    else:
        raise Exception(f"Untested combination of n and base: base = {base}, n = {n}")


def test_method__take_n_root__wrong_inputs():
    calc = c.Calculator()
    calc.reset(to=100)

    # Input is str instead of float:
    with py.test.raises(TypeError):
        calc.take_n_root("a")
    # Input is list instead of float:
    with py.test.raises(TypeError):
        calc.take_n_root([1])
    # Too many args:
    with py.test.raises(TypeError):
        calc.take_n_root(1, 2)


def test_method__sqrt__basic():
    calc = c.Calculator()
    calc.reset(to=100)
    calc.sqrt()
    assert calc.result == 10

    calc.reset(to=0)
    calc.sqrt()
    assert calc.result == 0


def test_method__exponentiate__basic():
    calc = c.Calculator()
    calc.reset(to=10)
    calc.exponentiate(3)
    assert calc.result == 1000


def test_method__add__basic():
    calc = c.Calculator()
    calc.add(5)
    assert calc.result == 5


def test_method__add__wrong_inputs():
    calc = c.Calculator()
    # Input is str instead of float:
    with py.test.raises(TypeError):
        calc.add("a")
    # Too many args:
    with py.test.raises(TypeError):
        calc.add(1, 2)


def test_method__subtract__basic():
    calc = c.Calculator()
    calc.subtract(15)
    assert calc.result == -15


def test_method__multiply_by__basic():
    calc = c.Calculator()
    calc.reset(to=-10)
    calc.multiply_by(-5)
    assert calc.result == 50


def test_method__divide_by__basic():
    calc = c.Calculator()
    calc.reset(to=50)
    calc.divide_by(5)
    assert calc.result == 10
