# Calculator
This calculator package can perform addition, subtraction, multiplication, and division, as well as taking a (n) root of a number and also resetting its memory. 

For each operation, it takes only one input number and combines it with the current value in its own memory, which can be reset to zero.

The technology stack for this project includes `Python` for building the package, `Docker` for containerizing the package, and `Pytest` for testing the package.

---
## Features

- Addition: The input value is added to the memory value.
- Subtraction: The input value is subtracted from the memory value.
- Multiplication: The input value is multiplied by the memory value.
- Division: The input value is divided by the memory value.
- Root: The input value root of the memory value is returned.
- Reset: The memory value is reset to zero.

---
## Installation

You can run any of the commands below to install the package.

### To install the package from PyPI

```shell
$ pip install calculatorvadim
```

### To install from github

```shell
$ pip install git+https://github.com/vadimiljin/calculatorvadim.git
```

### To get the calculator image from docker hub

```shell
$ docker pull iljinvadim/calculatorvadim
```

---
## Usage

Usage examples for each method are given below.

```python
>>> from calculatorvadim import Calculator
>>> calculator = Calculator()
>>> calculator.add(4)
4
>>> calculator.subtract(2)
2
>>> calculator.multiply(12)
24
>>> calculator.divide(3)
8.0
>>> calculator.root(3)
2.0
>>> calculator.reset()
0
```

---
## Testing

```shell
$ pytest
```

---
## License 

This project is licensed under the terms of the MIT license

---
## Author

Vadim Iljin