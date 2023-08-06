import pytest
from calculator.calc_mod import Calculator

calculator = Calculator() 

def test_add_simple():
    calculator.add(3) 
    assert calculator.get_current_val() == 3

def test_reset():
    calculator.reset()
    assert calculator.get_current_val() == 0

def test_add():
    calculator.add(3)
    calculator.add(5)
    calculator.add(10)
    calculator.add(-5) 
    calculator.add(0)
    assert calculator.get_current_val() == 13

def test_add_string():
    assert calculator.add("string") == TypeError  

def test_sub():
    calculator.sub(3) 
    calculator.sub(5)
    calculator.sub(-15)
    assert calculator.get_current_val() == 20

def test_sub_string():
    assert calculator.sub("string") == TypeError  

def test_div(): 
    calculator.div(4)  
    calculator.div(1/5)  
    calculator.div(5)   
    calculator.div(2.5)  
    assert calculator.get_current_val() == 2

def test_div_zero():
    assert calculator.div(0) == ZeroDivisionError 

def test_div_string():
    assert calculator.div("string") == TypeError

def test_mul(): 
    calculator.mul(3.5)  
    calculator.mul(10)  
    calculator.mul(0.1)  
    calculator.mul(7)  
    assert calculator.get_current_val() == 49

def test_mul_string(): 
    assert calculator.mul("string") == ValueError

def test_root(): 
    calculator.root(2)   
    assert calculator.get_current_val() == 7

def test_root_negative(): 
    calculator.reset()
    calculator.add(-125)  
    calculator.root(3)     
    assert calculator.get_current_val() == -5 
    calculator.add(-20)  
    assert calculator.root(2) == AssertionError
 
def test_root_string():
    assert calculator.root("string") == TypeError

def test_advanced(): 
    calculator.reset()
    calculator.add(50)   
    calculator.sub(25)  
    calculator.add(125) 
    calculator.div(5)   
    calculator.div(1/5)   
    calculator.mul(5.5)   
    calculator.sub(200)  
    current_val = calculator.get_current_val()
    calculator.mul(current_val)   
    calculator.mul(current_val)   
    calculator.root(3)
    calculator.mul(1/625)   
    calculator.div(3) 
    calculator.mul(1/3) 
    calculator.root(2)  
    assert calculator.get_current_val() == 1 / 3
    