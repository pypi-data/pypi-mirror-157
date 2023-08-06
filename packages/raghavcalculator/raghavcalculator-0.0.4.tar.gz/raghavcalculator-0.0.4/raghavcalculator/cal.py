import numpy as np
from bashplotlib.histogram import plot_hist

class Calculator:
    def add_numbers(num1, num2):
        return num1 + num2

    def subtract_numbers(num1, num2):
        return num1 - num2

    def multiply_numbers(num1, num2):
        return num1 * num2

    def divide_numbers(num1, num2):
        return num1 / num2
    
    def p():
        arr = np.random.normal(size=1000, loc=0, scale=1)
        return plot_hist(arr, bincount=50)
