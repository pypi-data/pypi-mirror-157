
# To solve this, we need to write a function that takes a string and returns the number
# of vowels in that string. We can then pass it to the `key` parameter of the `sorted`
# function to set the sort criteria.

# We can use a list comprehension to get a list of the vowel characters in a string
# `[c for c in 'string' if c in 'aeiou']`. From there we can use `len` to count
# them and we get our solution:

def num_vowels(name: str) -> int:
    return len([c for c in name if c in 'aeiou'])

sorted(fruit, key=num_vowels)