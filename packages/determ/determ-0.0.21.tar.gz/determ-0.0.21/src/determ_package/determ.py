# [C] Calvin Parsons - 2022
# Determ
vowels = ["a", "e", "i", "o", "u"]


# Declare function with required parameter 'to_determine' which is the data to be determined.
# temp_int is an optional input and is only required when determining a list (it is the list elements index)
def determiner(to_determine, temp_int=1):
    # If determiner is passed a string to determine.
    if type(to_determine) == str:
        # lower the first character of the string and check if it is a vowel or not
        if to_determine[0].lower() in vowels:
            # The first character is a vowel.
            return 'an ' + to_determine
        else:
            # The first character is not a vowel.
            return 'a ' + to_determine
    # If determiner is passed a list & a element index to determine.
    elif type(to_determine) == list:
        # lower the first character of the requested element and check if it is a vowel or not
        if to_determine[temp_int][0].lower() in vowels:
            # The first character is a vowel.
            return 'an ' + to_determine[temp_int]
        else:
            # The first character is not a vowel.
            return 'a ' + to_determine[temp_int]
    else:
        return 'can not determine this datatype'

