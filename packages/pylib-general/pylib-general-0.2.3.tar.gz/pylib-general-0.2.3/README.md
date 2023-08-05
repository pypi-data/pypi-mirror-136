# PyLib - General

This is a package that will be updated whenever I get an idea that I like and write it.

So far, I have:
- [Properties](#properties)
- [Num](#num)
- [Text](#text)
- [Exceptions](#exceptions)


## Properties

This can be used like:

`from pylib_general import properties`
`import pylib_general.properties as properties`

This loads the Property class, which can be used like:

`varname = properties.Property()`

The property class's functions are:

- `varname.add(name, val)`

`name` being the name of the new value (cannot contain spaces), and `val` being the value.

- `varname.remove(name)`
`name` being the name of the value to remove

- `varname.get(name)`
returns the value of `name`

The difference between Property and other sets is that you can get a property in a much easier way:

`varname.attr`

Obviously, you can also get a value through `varname.get(name)` but you could also do `varname.name`

Ex:

```
varname = Property().add("somenamenotcontainingnumbersorspaces", "12233090")
print(varname.somenamenotcontainingnumbersorspaces)
```
prints `12233090`

A hidden way to get values is `varname.__dict__["name"]` (Not preferable)

calling that, `varname.attr`, `del varname.attr`, or `varname.attr = val` will call the get, remove, and add functions respectively.

## Num

This can be used like:

`from pylib_general import num`
`import pylib_general.num as num`

This loads the number functions, which are:

- `num.factorial(n)`

Where `n` is the number you want to factorial, returns n!

- `num.sig(n)`

Where `n` is the number you want to sigma, returns n + (n-1) + (n-2) ...

- `num.pow(n, p)`

Where `n` is the number you want to raise to the power of `p`. Returns n^p (python syntax: `n**p`)

- `num.incr(n)`

Where `n` is the number to increment by 1. Returns n + 1

- `num.decr(n)`

Where `n` is the number to decrement by 1. Returns n - 1

- `num.mod(n, d)`

Where `n` is the number to modulo with `d`. Returns n % d

- `num.get_fibo(terms)`

Where terms is the number of terms of the Fibonacci sequence you want to get. Returns array.
Special usage: `get_fib(3)[2]` will return 1, same as `_recur_fib(2)` (preferably not used)

- `num.pi`

Equals 22/7

## Text

This can be used like:

`from pylib_general import text`
`import pylib_general.text as text` 

- `text.checkstr(ost)`

Checks if `ost` is a string or not. returns True or False.

- `text.rev(ost)`

Returns the reverse of the string `ost`

- `text.ascii_convert(ost)`

Takes `ost` and converts it's characters into their ascii codes separated with hyphens (dashes). Returns string.
Ex: `text.ascii_convert("ccC")` returns "99-99-67"

- `text.caesarcipher(ost, key=1)`

Takes `ost` and shifts the characters by a key, giving the [Caesar Ciphered](https://www.wikipedia.org/wiki/Caesar_cipher) version of it as a string.
Ex: `text.caesarcipher("ccC")` returns "ddD"

- `text.weirdcase(ost)`

Takes `ost` and makes every other letter uppercase.
Ex: `text.weirdcase("ccced")` returns "CcCeD"
Note: if instead of "CcCeD" you want "cCcEd," you can use `text.weircase("ccced").swapcase()`

- `text.encode(ost, key=1)`

Ah, here is the masterpiece of the text module: encode! It takes `ost` and reverses the the ascii version of the weirdcase of the caesarcipher of `ost.`
The code for the return value is `rev(ascii_convert(weirdcase(caesarcipher(ost, key))))`
Ex: `text.encode("ccC")` returns "86-001-86"

- `text.checkpalindrome(ost)`

Takes `ost` and checks if it is a [palindrome](https://en.wikipedia.org/wiki/Palindrome).

## Exceptions

This can be used like:

`from pylib_general import exceptions`
`import pylib_general.exceptions as exceptions`

- `exceptions.Error`

Literally just an exception, except under a different name.

- `exceptions.NumTooLowError(value, message="Value was too low.")`

when [raised](https://www.w3schools.com/python/ref_keyword_raise.asp), shows `exceptions.NumTooLowError: 112: Value was too low.` (assuming the value parameter was 112)

- `exceptions.NumTooHighError(value, message="Value was too high.")`

when raised, shows `exceptions.NumTooHighError: 112: Value was too high` (assuming the value parameter is 112)

- `exceptions.NumNotInRangeError(nrange, value, message="Value not in range ")`

when raised correctly, shows `exceptions.NumNotInRangeError: 112: Value not in range (2, 99)` (assuming the nrange passed was [2, 99] and the value passed was 112)
