from decimal import DivisionByZero
import py.test
import unittest
from arithmetic_calc import Arithmetic

class TestCalculatorMethods(unittest.TestCase):

    def test_add(self):
        calc = Arithmetic()
        self.assertEqual(calc.add(2, 3.0), 5.0)
        self.assertEqual(calc.add(-1), 4.0)
    
    def test_substraction(self):
        calc = Arithmetic()
        self.assertEqual(calc.substract(2, 3.0), -1.0)
        self.assertEqual(calc.substract(-1), 0.0)
    
    def test_multiplication(self):
        calc = Arithmetic()
        self.assertEqual(calc.multiply(2, 3.0), 6.0)
        self.assertEqual(calc.multiply(-1), -6.0)
    
    def test_divide(self):
        calc = Arithmetic()
        self.assertAlmostEqual(calc.divide(2, 3.0), 0.6666666666666666)
        self.assertAlmostEqual(calc.divide(-1), -1.5)
    
    def test_root(self):
        calc = Arithmetic()
        self.assertAlmostEqual(calc.root(2, 2), 1.4142135623730951)
    
    def test_all_arithmetic(self):
        calc = Arithmetic()
        self.assertEqual(calc.add(2, 3), 5)
        self.assertEqual(calc.add(10), 15)
        self.assertEqual(calc.substract(10, 3.0), 7.0)
        self.assertEqual(calc.substract(2), -5.0)
        self.assertEqual(calc.add(10), 5.0)
        self.assertEqual(calc.multiply(-1), -5.0)


if __name__ == "__main__":
    test = TestCalculatorMethods()
    test.test_add()
    test.test_substraction()
    test.test_divide()
    test.test_multiplication()
    test.test_root()
    test.test_all_arithmetic()