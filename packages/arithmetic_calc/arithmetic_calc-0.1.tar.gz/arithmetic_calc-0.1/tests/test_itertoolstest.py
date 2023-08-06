from itertools import permutations, combinations
import unittest

from arithmetic_calc import Arithmetic

class ItertoolsTesting():

    def test_add(self):
        calc = Arithmetic()
        args = [0.8, 0, -0.4, 1, 2, -1, 5, 9, -9]
        for t in permutations(args, 2):
            num1, num2 = t
            calc.add(num1, num2)
            calc.substract(num1, num2)
            if num2 != 0:calc.divide(num1, num2)
            calc.multiply(num1, num2)

if __name__ == "__main__":
    test = ItertoolsTesting()
    test.test_add()