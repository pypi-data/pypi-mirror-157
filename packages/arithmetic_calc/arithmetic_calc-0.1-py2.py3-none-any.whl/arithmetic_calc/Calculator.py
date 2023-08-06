import math
from typing import Optional

class Arithmetic:
    '''
    Name
        Arithmetic
    Description
        This module provides access to arithmetic operations
    '''
    def __init__(self) -> None:
        ''' Instantiate a calculator

        '''
        self.memo = 0.0

    def add(self, num1:float, num2:Optional[float] = None)->float:
        ''' Compute sum of two numbers num1, and num2

        Example 1 (both num1, and num2 given):

            >>> result = calc.add(num1 = 5.0, num2 = 4.0)
            >>> result 
            9.0

        Example 2 (only one parameter is given, and the second parameter would be value in memory):
            As a result of execution of the above example, the value in the memory is now 9.0

            >>> result = calc.add(num1 = 5.0)
            >>> result 
            14.0
        '''

        num2 = num2 if num2 != None else self.memo
        result = num1 + num2
        self.memo = result
        return self.memo

    def substract(self, num1:float, num2:Optional[float] = None)->float:
        ''' Compute substraction of two numbers num1, and num2

        Example 1 (both num1, and num2 given):

            >>> result = calc.substract(num1 = 5.0, num2 = 4.0)
            >>> result 
            1.0

        Example 2 (only one parameter is given, and the second parameter would be value in memory):
            As a result of execution of the above example, the value in the memory is now 1.0

            >>> result = calc.substract(num1 = 5.0)
            >>> result 
            4.0
        '''
        num2 = num2 if num2 != None else self.memo
        result = num1 - num2
        self.memo = result
        return self.memo

    def multiply(self, num1:float, num2:Optional[float] = None)->float:
        ''' Compute multiplication of two numbers num1, and num2

        Example 1 (both num1, and num2 given):

            >>> result = calc.multiply(num1 = 5.0, num2 = 4.0)
            >>> result 
            20.0

        Example 2 (only one parameter is given, and the second parameter would be value in memory):
            As a result of execution of the above example, the value in the memory is now 20.0

            >>> result = calc.multiply(num1 = 5.0)
            >>> result 
            100.0
        '''
        num2 = num2 if num2 != None else self.memo
        result = num1 * num2
        self.memo = result
        return self.memo

    def divide(self, num1:float, num2:Optional[float] = None)->float:
        ''' Compute division of two numbers num1, and num2

        Example 1 (both num1, and num2 given):

            >>> result = calc.divide(num1 = 1.0, num2 = 3.0)
            >>> result 
            0.3333333333333333

        Example 2 (only one parameter is given, and the second parameter would be value in memory):
            As a result of execution of the above example, the value in the memory is now 2.0

            >>> result = calc.divide(num1 = 5.0)
            >>> result 
            15.0
        '''
        num2 = num2 if num2 != None else self.memo
        result = num1/num2
        self.memo = result
        return self.memo
    
    def root(self, num:float, root:float )->float:
        ''' Compute root of a number

        Example 1:
            >>> result = calc.root(8.0,2)
            >>> result
            2.8284271247461903
        
        Example 2: 
            >>> result = calc.root(-4, 2)
            >>> result
            (1.2246467991473532e-16+2j)
        '''
        result =  pow(num, 1/root)
        self.memo = result
        return self.memo

    def reset_memory(self, memo:Optional[float]=0.0)->None:
        ''' Resets memory of calculator

        Example 1(given new value in the memory):

                >>> calc.reset_memory(2.0)
                >>> calc.memo
                2.0

        Example 2 (given a new value in the memory to be default values)
                >>> calc.reset_memory()
                >>> calc.memo
                0.0
        '''
        self.memo = memo

if __name__ == "__main__":
    import doctest
    calc  = Arithmetic()
    print(doctest.testmod())