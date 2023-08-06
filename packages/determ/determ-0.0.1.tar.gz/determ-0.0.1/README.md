Determ
=======================================================
Determ is a simple module which automatically appends the correct determiner to a given string or list element.
Only one function is required `determiner` but what it does depends on the datatype supplied.

Determiner can only determine lists and strings. It will attempt to gracefully handle an exception if any other datatype is supplied.

Feature Overview
----------------
Example usage with a string:

Supply determ's determiner function with a string you want to determine. 
```Python
import determ
# Passing determ a string to determine.
test_consonant = "fish"
test_vowel = "aardvark"
# This is not a list or string so will throw an exception when determ attemps to determine it.
test_exception = 1
print("String determ test consonant: " + determ.determiner(test_consonant))
print("String determ test vowel: " + determ.determiner(test_vowel))
print("String determ test exception: " + determ.determiner(test_exception))
```
Output:
```
String determ test consonant: a fish
String determ test vowel: an aardvark
String determ test exception: can not determine this datatype
```

Example usage with a list:

Supply the determ's determiner function with a list and the element index want to determine.
```Python
import determ
list = ['fish', 'dog', 'cat', 'aardvark']
for i in range(0, len(list)):
    print(str("Element ") + str(i) + str(" determined: ") + determ.determiner(list, i))
```
Output:
```
Element 0 determined: a fish
Element 1 determined: a dog
Element 2 determined: a cat
Element 3 determined: an aardvark
```

Main Features
-------------
- Add something here - `fancy code`
    
Installation
------------
On all operating systems, the latest stable version of `determ` can be installed using pip:

```bash
pip install -U determ
```

determ works with Python 3.6+ on Windows, macOS, and Linux. It is pure Python code with no 3rd-party dependencies.


Documentation
-------------
The latest documentation for determ can be read online here: https://determiner.readthedocs.io/en/latest/

It is available in HTML, PDF, and ePub formats.



