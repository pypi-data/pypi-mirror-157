import pytest
import calculatorvadim


def test_add():
    calc = calculatorvadim.Calculator()
    assert calc.add(4) == 4, "Addition method fails"


def test_subtract():
    calc = calculatorvadim.Calculator(4)
    assert calc.subtract(2) == 2, "Subtraction method fails"


def test_multiply():
    calc = calculatorvadim.Calculator(4)
    assert calc.multiply(4) == 16, "Multiply method fails"


def test_division():
    calc = calculatorvadim.Calculator(4)
    assert calc.divide(2) == 2, "Division method fails"


def test_root():
    calc = calculatorvadim.Calculator(8)
    assert calc.root(3) == 2, "Root method fails"


def test_reset():
    calc = calculatorvadim.Calculator(5)
    assert calc.reset() == 0, "Reset method fails"


def test_type_error():
    calc = calculatorvadim.Calculator(5)
    with pytest.raises(TypeError) as error:
        calc.add("Foo")
    assert str(error.value.args[0]) == "Please enter a valid number!"


def test_division_by_zero():
    calc = calculatorvadim.Calculator(5)
    with pytest.raises(ZeroDivisionError) as error:
        calc.divide(0)
    assert str(error.value.args[0]) == "Dividing by zero is not a valid operation!"


def test_validate_init_method():
    with pytest.raises(ValueError) as error:
        calculatorvadim.Calculator("Bar")
    assert (
        str(error.value.args[0])
        == "Please enter a valid number for the calculator's memory value!"
    )


def test_complex_number():
    calc = calculatorvadim.Calculator(-9)
    with pytest.raises(ValueError) as error:
        calc.root(2)
    assert (
        str(error.value.args[0])
        == "The root of a complex or negative number is not allowed."
    )
