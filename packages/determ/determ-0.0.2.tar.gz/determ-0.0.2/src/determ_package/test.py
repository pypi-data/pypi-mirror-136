# [C] Calvin Parsons - 2022
# Determ
import determ

# Passing determ a string to determine.
test_consonant = "fish"
test_vowel = "aardvark"
# This is not a list or string so will throw an exception when determ attemps to determine it.
test_exception = 1
print("String determ test consonant: " + determ.determiner(test_consonant))
print("String determ test vowel: " + determ.determiner(test_vowel))
print("String determ test exception: " + determ.determiner(test_exception))

# Passing determ a list and the list element index to determine.
list = ['fish', 'dog', 'cat', 'aardvark']
for i in range(0, len(list)):
    print(str("Element ") + str(i) + str(" determined: ") + determ.determiner(list, i))

