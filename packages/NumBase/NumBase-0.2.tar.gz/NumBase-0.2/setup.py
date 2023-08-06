from setuptools import setup


with open('README.md') as f:
    long_description = f.read()

          
long_description = """A class for translating numbers from different number systems to any other
number system up to the hexadecimal number system and performing basic
arithmetic operations with numbers in different
and identical number systems"""
          
setup(name="NumBase",
     version="0.2",
     author="lemme-hype",
     author_email="terekhova.kris98@gmail.com",
     description="Arithmetic operations of numbers with different number systems",
     licence ="Apache Lecense, Version 2.0, see Lecense file",
     packages = ['NumBase'],
     python_requires=">=3.6")    
