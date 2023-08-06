import math
import py.test
from hypothesis import given, assume, strategies as st
from decimal import DivisionByZero, DivisionImpossible


from arithmetic_calc import Arithmetic

# test for type and domain error
def test_division():
    calc = Arithmetic()
    with py.test.raises(ZeroDivisionError):
        calc.divide(2, 0)
def test_root():
    calc = Arithmetic()
    with py.test.raises(ZeroDivisionError):
        calc.root(-1, 0)

def test_type_error():
    calc = Arithmetic()
    with py.test.raises(TypeError):
        calc.add(2, '3')
    
    with py.test.raises(TypeError):
        calc.add(2, 3, 4)

# test using hyphotesis libray module
@given(
    st.floats(min_value = -100000000, max_value = 100000000),
    st.floats(min_value = -100000000, max_value = 100000000),
    # st.floats(),
    # st.floats(),
)
def test_calculator_hypho(a, b):
    calc = Arithmetic()
    assume(abs(a) >= 0.0001)
    assume(abs(b) >= 0.0001)

    result = calc.add(a, b)
    assert math.isclose(result, math.fsum([a,b]), abs_tol=(0.001))

    result = calc.substract(a, b)
    assert math.isclose( math.fsum([result, b]), a, abs_tol=(0.001))

    result = calc.multiply(a, b)
    assert math.isclose(a*b, result, abs_tol=(0.0001))

    result = calc.divide(a, b)
    assert math.isclose(result, a/b, abs_tol=(0.001))
    assert result == calc.memo
    
    assert math.isclose(calc.root(4, 2), 2)