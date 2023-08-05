# pyclassifier
A Python module to create classes and objects out of dictionaries.

``` PYTHON
from pyclassifier import dictionary
Dictionary = {'a':1,'b':{'c':3}}
Variable = dictionary(Dictionary)
print(Dictionary['b']['c'])
print(Variable.b.c)
```
