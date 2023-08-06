Arithmetic Calculator
=====================
A simple program which performs arithmetic operation.

Arithmetic_calculator performs operation such as:
<ul>
  <li>Addition/Substraction</li>
  <li>Divistion/Multiplication</li>
  <li>Take(n) root of a number</li>
</ul>

Installation
------------

It can be installed with::
```
pip install arithmetic_calc
```

Usage
-----
To use arithmetic_calculator, we first create an object
```
from arithmetic_calculator import Arithmetic()
calc = Arithmetic()
```
Addition of two numbers
```
result = calc.add(2, 3)
result = 5
```
Addition of a number to the value in memory
```
result = calc.add(1)        #same as result = calc(1, 5)
result = 6                  # 5 is value of number from memory
```
Substraction
```
result = calc.substract(4, 2)
result = 2
```
Divisio
```
result = calc.divide(4, 2)
result = 2.0
```
Multiplication
```
result = calc.multiply(2, 3)
result = 6
```
Root(n) of num
```
result = calc.root(9,2)
result = 3
```
Author
------------
Ibsa Abraham
