"""
This is my first experience creating a simple python calculator module.

Let's calculate!
"""

__version__ = "0.0.4"


class Calculator:
    """
    This class represents a calculator.

    ...

    Attributes
    ----------
    memory_value : float
        value in calculator memory
    """

    def __init__(self, memory_value: float = 0):
        self._memory_value = self._validate_memory_value(memory_value)
        """
        This method constructs the necessary attributes for the calculator object.

        Parameters
        ----------
        memory_value : float
            value of the memory
        """

    def add(self, input_value: float) -> float:
        """This method accepts a value and increments it by the value currently stored in memory, returning the new value."""
        self._validate_input(input_value)
        self._memory_value += input_value
        return self._memory_value

    def subtract(self, input_value: float) -> float:
        """This method accepts a value and subtracts it from the value stored in memory, returning the difference."""
        self._validate_input(input_value)
        self._memory_value -= input_value
        return self._memory_value

    def multiply(self, input_value: float) -> float:
        """This method takes in a value and multiplies it with the value in memory, returning the multiplication."""
        self._validate_input(input_value)
        self._memory_value *= input_value
        return self._memory_value

    def divide(self, input_value: float) -> float:
        """This method takes in a value and divides it by the value in memory, returning the division."""
        self._validate_input(input_value)
        self._division_by_zero(input_value)
        self._memory_value /= input_value
        return self._memory_value

    def root(self, input_value: float) -> float:
        """This method takes in a value n and returns the nth root of the value stored in memory."""
        self._validate_input(input_value)
        self._division_by_zero(input_value)
        self._complex_number_for_root(input_value)
        self._memory_value = self._memory_value ** (1.0 / input_value)
        return self._memory_value

    def reset(self) -> float:
        """This method will set the value stored in memory to zero."""
        self._memory_value = 0
        return self._memory_value

    def _validate_memory_value(self, new_value: float) -> float:
        if not isinstance(new_value, (int, float)):
            raise ValueError(
                "Please enter a valid number for the calculator's memory value!"
            )
        self._memory_value = new_value
        return self._memory_value

    def _validate_input(self, input_value: float) -> float:
        if isinstance(input_value, (int, float)):
            return input_value
        raise TypeError("Please enter a valid number!")

    def _division_by_zero(self, input_value: float) -> float:
        if input_value == 0:
            raise ZeroDivisionError("Dividing by zero is not a valid operation!")
        return input_value

    def _complex_number_for_root(self, input_value: float) -> float:
        if self._memory_value < 0:
            raise ValueError("The root of a complex or negative number is not allowed.")
        return input_value
