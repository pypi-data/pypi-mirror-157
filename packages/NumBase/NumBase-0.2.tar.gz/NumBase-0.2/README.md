# NumBase Class

A class for translating numbers from different number systems to any other
number system up to the hexadecimal number system and performing basic
arithmetic operations with numbers in different
and identical number systems
Attributes:
number (str), input number
base (int) its input system
TODO: Complete all functions below

### Methods defined here:

### to_decimal
Method converts a number from any other system up to and including hexadecimal to decimal system      
Args: number, base
Returns: str

### from_decimal
Method converts a number from the decimal system to any other system up to and including hexadecimal        
Args: number, base
Returns: str

### add
Method is used to add the numbers from two different number systems by first converting them to the decimal system and then returns it into the system specified in the argument base
Args: number, base
Returns: str

### sub
Method is used to subtract the numbers from two different number systems by first converting them to the decimal system and then returns it into the system specified in the argument base
Args: number, base
Returns: str

### mul
Method is used to multiply the numbers from two different number systems by first converting them to the decimal system and then returns it into the system specified in the argument base
Args: number, base
Returns: str

### truediv
Method is used to divide the numbers from two different number systems by first converting them to the decimal system and then returns it into the system specified in the argument base
Args: number, base
Returns: str

### pow
Method is used to raise to a power the numbers from two different number systems by first converting them to the decimal system and then returns it into the system specified in the argument base
Args: number, base
Returns: str

### mod
Method is used to get the remainder of the division of the numbers from two different number systems by first converting them to the decimal system and then returns it into the system specified in the argument base
Args: number, base
Returns: str

### Other methods are magical methods


