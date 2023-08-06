class Calculator: 
    def __init__(self):
        """ Initializes the starting value to 0 """ 
        self.current_val = 0 

    def get_current_val(self):
        return self.current_val
    
    def add(self, number):  
        """ Adds a number to the current_val
            and raises an exception if non numeric value is entered """ 
        try: 
            self.current_val = self.__fix_type__(self.current_val + number)
            return self.current_val 
        except TypeError as e:
            print("Exception occurred:", e)   
            return TypeError

    def sub(self, number):
        """ Subtracts a number from the current_val
            and raises an exception if non numeric value is entered """ 
        try:
            self.current_val = self.__fix_type__(self.current_val - number)
            return self.current_val
        except TypeError as e:
            print("Exception occurred:", e)
            return TypeError

    def div(self, number):
        """ Divides current_val by a number
            and raises an exception if non numeric value is entered or division is by 0 """ 
        try:
            self.current_val = self.__fix_type__(self.current_val / number)
            return self.current_val 
        except TypeError as e:
            print("Exception occurred:", e) 
            return TypeError
        except ZeroDivisionError:
            print("Division by zero is impossible.") 
            return ZeroDivisionError

    def mul(self, number):
        """ Multiplies the current_val by a number
            and raises an exception if non numeric value is entered """ 
        try:
            self.current_val = self.__fix_type__(self.current_val * number)
            return self.current_val 
        except ValueError:
            print("Exception occurred: Value has to be a valid number") 
            return ValueError

    def reset(self):
        """ Resets the current_val to 0 """ 
        self.current_val = 0
        return self.current_val 

    def root(self, n):
        """ Takes the nth root of a number """     
        try:  
            """ Root procedures with negative number and equal roots does not give a real root
                Therefore, the assertion error is thrown if user inputs such value. """
            assert self.current_val >= 0 or (self.current_val < 0 and n % 2 != 0)
            negative = False

            if self.current_val < 0:
                negative = True
                self.current_val *= -1
            
            self.current_val = self.current_val**(1/n) 
  
            fraction = self.current_val % 1    

            """ Checks if the fraction is long or periodic
                * f_tenths - takes the tenths decimal number
                * f_hundredths - takes the tenths decimal number """       
            if len(str(fraction)) > 3:
                f_tenths = float (str (fraction)[:-(len(str(fraction)) - 3)])
                f_hundredths = float (str (fraction)[:-(len(str(fraction)) - 4)])
                
                if f_tenths == 0.9: 
                    """ Fixes fraction with repeating nines after decimal point .99999 """   
                    self.current_val = round(self.current_val) 
                elif f_hundredths == 0: 
                    """ Fixes fraction with repeating zeroes after decimal point .000 """ 
                    self.current_val = round(self.current_val, 5)
            
            if negative:
                self.current_val *= -1

            return self.__fix_type__(self.current_val)

        except TypeError as e:
            print("Exception occurred:", e) 
            return TypeError
        except AssertionError:
            print("Negative numbers don't have real roots with equal numbers.") 
            return AssertionError

    def __fix_type__(self, number):
        """ Help function for fixing number type.
            If number is an integer of type float (example: 10.0) - changes its type back to int (10) """ 
        if isinstance(number, float): 
            if number.is_integer(): 
                number = int(number)
        else:
            number = int(number) 

        return number 