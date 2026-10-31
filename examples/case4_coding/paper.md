# Programming and Mathematics Assignment

Submit your work as one zip file. Name each file after its question, for example `q1.py`,
`q2.py`, `q3.py` and `q4_report.docx`. Use only the Python standard library. Total: 30 marks.

## Q1. Palindromes (6 marks)

Write a function `is_palindrome(s)` that returns `True` if the string `s` reads the same forwards
and backwards when case, spaces and punctuation are ignored, and `False` otherwise. The empty
string is a palindrome. For example, `is_palindrome("A man, a plan, a canal: Panama")` is `True`.

## Q2. FizzBuzz (6 marks)

Write a function `fizzbuzz(n)` that returns a list of strings for the numbers 1 to `n`: `"Fizz"` for
multiples of 3, `"Buzz"` for multiples of 5, `"FizzBuzz"` for multiples of both, and the number as a
string otherwise. `fizzbuzz(0)` returns an empty list.

## Q3. Mean and spread (8 marks)

Write a function `mean_std(values)` that returns a tuple `(mean, standard deviation)` of a list of
numbers, using the population standard deviation (divide by the number of values). Raise a
`ValueError` if the list is empty.

## Q4. Report: the quadratic formula (10 marks)

In a short report, derive the quadratic formula for a x^2 + b x + c = 0 (a not equal to 0) by
completing the square. Then solve x^2 - 5x + 6 = 0 with it, and explain what the discriminant
b^2 - 4ac tells you about the roots. Show your equations.
