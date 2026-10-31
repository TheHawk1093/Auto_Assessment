# Marking schemes: Programming and Mathematics Assignment (30 marks)

## Question 1 (6 marks, code)

Q1. Palindromes (6 marks)

Write a function `is_palindrome(s)` that returns `True` if the string `s` reads the same forwards and backwards when case, spaces and punctuation are ignored, and `False` otherwise. The empty string is a palindrome. For example, `is_palindrome("A man, a plan, a canal: Panama")` is `True`.

```
Marking stance: standard. Full marks need all three points: the cleaned text keeps only letters and digits in lower case (3), it is compared with its reverse on the cleaned text (2), and the function returns True for the empty string and returns a boolean (1). Each point is all or nothing because the teacher's rubric gives no part-mark levels. Any correct implementation earns the marks, and the student does not need to match the model answer's code.
P1 (3 marks): Builds a cleaned version of s that keeps only letters and digits (spaces and punctuation removed, e.g. using ch.isalnum(), or an equivalent filter) AND ignores case (e.g. lower-casing or case-folding each kept character). Both parts are required for the full 3 marks. Accept any equivalent method, such as a regex that removes non-alphanumerics and lowercases. Do not award these marks if the code only removes spaces, or only lowercases without removing punctuation, or compares the raw string.
P2 (2 marks): Decides palindrome status by comparing the cleaned text with its reverse, e.g. cleaned == cleaned[::-1], or an equivalent reversed comparison or two-pointer check on the cleaned text. The comparison must be made on the cleaned text, not the original s. Accept any correct equivalent method.
P3 (1 marks): Handles the empty string (or a string with no letters or digits) correctly so that it returns True, and returns a boolean (True/False) result from the function. This is earned naturally by a correct cleaned-and-compare approach, but the student must return True/False and not, for example, a string, a count, or None. Do not award if the code crashes or wrongly returns False for the empty string.
```

## Question 2 (6 marks, code)

Q2. FizzBuzz (6 marks)

Write a function `fizzbuzz(n)` that returns a list of strings for the numbers 1 to `n`: `"Fizz"` for multiples of 3, `"Buzz"` for multiples of 5, `"FizzBuzz"` for multiples of both, and the number as a string otherwise. `fizzbuzz(0)` returns an empty list.

```
Marking stance: standard. Full marks need a loop covering 1 to n inclusive, the FizzBuzz test placed before the Fizz and Buzz tests, and correct exact outputs including an empty list for 0. Each of the three points is all or nothing, as the teacher's rubric gives no part-mark steps. Answers that test Fizz or Buzz before FizzBuzz, or that use the wrong loop range, lose the corresponding points, while any correct implementation earns full marks.
P1 (2 marks): The function loops over the integers 1 to n inclusive, so n itself is included and 1 is the first value (e.g. `range(1, n + 1)` or an equivalent). Looping only to n-1 (e.g. `range(1, n)`), starting at 0, or otherwise leaving out or adding values earns no credit for this point.
P2 (2 marks): The multiple-of-both case is tested first, before the single-divisor cases: the check for FizzBuzz (e.g. `i % 15 == 0`, or `i % 3 == 0 and i % 5 == 0`) comes before the checks for Fizz and Buzz. If Fizz or Buzz is tested first so that FizzBuzz can never be produced, this point earns no credit, even if FizzBuzz is written in the code.
P3 (2 marks): The output is correct for each case: multiples of 3 (not 5) give "Fizz", multiples of 5 (not 3) give "Buzz", other numbers give the number as a string (e.g. `str(i)`), and `fizzbuzz(0)` returns an empty list (e.g. `[]`, not None or an error). The strings must match exactly, including capitalisation and no spaces. The result is a list of strings, not integers. Any error in these outputs means this point earns no credit.
```

## Question 3 (8 marks, code)

Q3. Mean and spread (8 marks)

Write a function `mean_std(values)` that returns a tuple `(mean, standard deviation)` of a list of numbers, using the population standard deviation (divide by the number of values). Raise a `ValueError` if the list is empty.

```
Marking stance: standard. Full marks need all four points: correct mean, population standard deviation (divide by n, then square root), a ValueError for an empty list, and a (mean, std) tuple. Each point is all or nothing, as the teacher's rubric gives no part-mark levels. A wrong divisor (n-1) loses the standard deviation marks but not the mean or other points, and a correct std with a wrong mean still loses only the mean mark.
P1 (2 marks): Computes the mean correctly as the sum of the values divided by the number of values (e.g. sum(values) / len(values) or an equivalent loop). Dividing by n-1 or using any other divisor is wrong.
P2 (3 marks): Computes the population standard deviation: the mean of the squared deviations from the mean, dividing by the number of values n (not n-1), then takes the square root (e.g. math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))). Using n-1 (sample standard deviation) or omitting the square root does not earn this mark.
P3 (2 marks): Raises a ValueError when the list is empty, checking before any division by the length (e.g. if not values: raise ValueError(...)). Raising a different exception type, or failing with ZeroDivisionError on an empty list, does not earn this mark.
P4 (1 marks): Returns a tuple in the order (mean, standard deviation), e.g. return mean, std or return (mean, std). Returning a list, or the values in the reverse order, does not earn this mark.
```

## Question 4 (10 marks, essay)

Q4. Report: the quadratic formula (10 marks)

In a short report, derive the quadratic formula for a x^2 + b x + c = 0 (a not equal to 0) by completing the square. Then solve x^2 - 5x + 6 = 0 with it, and explain what the discriminant b^2 - 4ac tells you about the roots. Show your equations.

```
Marking stance: standard. Each point is a single checkable step and is all or nothing, following the teacher's mark allocation: derivation 4 marks (P1–P4), solving the example 3 marks (P5), and the three discriminant cases 3 marks (P6–P8). Full marks need every derivation step, both roots 2 and 3 with the working shown, and all three discriminant cases stated correctly. The teacher's rubric gives no part-mark levels, so the marker should award each point in full or not at all.
P1 (1 marks): Divides the whole equation by a (a ≠ 0) to get x² + (b/a)x + c/a = 0 (or an equivalent form such as x² + (b/a)x = −c/a after moving c/a across). Dividing by a must be shown, not assumed.
P2 (1 marks): Completes the square by adding (b/2a)² (or (b/2a)² written in any equivalent form) to both sides of the equation. Adding a different term, or adding it to one side only, does not earn this mark.
P3 (1 marks): Writes the left side as a perfect square and simplifies the right side correctly to give (x + b/2a)² = (b² − 4ac)/(4a²), or an equivalent correct form such as (2ax + b)² = b² − 4ac. Any arithmetic error in the right side means no mark.
P4 (1 marks): Takes the square root of both sides, including the ± sign, and rearranges to reach x = (−b ± √(b² − 4ac)) / (2a) or an equivalent correct form. Omitting the ± sign means no mark.
P5 (3 marks): Solves x² − 5x + 6 = 0 correctly: identifies a = 1, b = −5, c = 6, substitutes into the formula (or an equivalent method such as factorising) and states both roots, x = 2 and x = 3. Both roots must be stated correctly to earn the 3 marks. Any other pair of roots, or a single root only, earns no mark for this point.
P6 (1 marks): States that when b² − 4ac > 0 (positive discriminant) the equation has two distinct real roots. Phrasing such as 'two different real solutions' is acceptable.
P7 (1 marks): States that when b² − 4ac = 0 the equation has exactly one repeated (equal) real root. Phrasing such as 'one real solution' or 'the two roots coincide' is acceptable.
P8 (1 marks): States that when b² − 4ac < 0 (negative discriminant) the equation has no real roots, and may add that the roots are a complex conjugate pair. Saying the roots are 'imaginary' or 'complex' without saying there are no real roots does not earn this mark.
```
