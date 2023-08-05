import pytest
import itertools

import sys
sys.path.append(r'G:\My Drive\TC_projects\m1_s1_project')

from pycalc3.calculator import Calculator

def test_calculator():
    cal = Calculator()

    cal.add(10)
    assert cal.memory_value == 10

    cal.subtract(2)
    assert cal.memory_value == 8

    cal.multiply(4)
    assert cal.memory_value == 32

    cal.divide(2)
    assert cal.memory_value == 16

    cal.reset()
    assert cal.memory_value == 0

    cal.add(9)
    cal.root(2)
    assert cal.memory_value == 3

    method_list = ['add', 'subtract', 'multiply', 'divide', 'root', 'reset']

    input_values = [0, 1, 4, 0.5, -3, 7]

    for method_names in itertools.permutations(method_list):
        for input_values in itertools.permutations(input_values):
            for method_name, input_value in zip(method_names, input_values):
                if method_name == 'add':
                    cal.add(input_value)

                if method_name == 'subtract':
                    cal.subtract(input_value)

                if method_name == 'multiply':
                    cal.multiply(input_value)

                if method_name == 'divide':
                    cal.divide(input_value)

                if method_name == 'root':
                    cal.root(input_value)

                if method_name == 'reset':
                    cal.reset()