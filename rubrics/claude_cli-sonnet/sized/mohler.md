# mohler: sized rubrics

Marks per point add up to the question total.

## mohler/E01.Q03 (5 marks)

**Question:** What are the main advantages associated with object-oriented programming?

**Model answer:** Abstraction and reusability.

- **P1** (2.5): States abstraction as an advantage of object-oriented programming (equivalent wording, e.g. hiding complexity/implementation detail behind objects and classes, earns the mark).
- **P2** (2.5): States reusability as an advantage of object-oriented programming (equivalent wording, e.g. code can be reused via classes/inheritance, earns the mark).


## mohler/E01.Q05 (5 marks)

**Question:** What is a variable?

**Model answer:** A location in memory that can store a value.

- **P1** (3): States that a variable is a location in memory (a named storage location/space in the computer's memory). Equivalent wording accepted.
- **P2** (2): States that it stores/holds a value (data) that can be used or changed.


## mohler/E02.Q02 (5 marks)

**Question:** What is the difference between a data member and a local variable inside a member function?

**Model answer:** Data members can be accessed from any member functions inside the class defintion. Local variables can only be accessed inside the member function that defines them.

- **P1** (2.5): States that data members can be accessed by any/all member functions of the class (they belong to the class/object and are available throughout the class definition).
- **P2** (2.5): States that local variables can only be accessed within the single member function that defines them (their scope is limited to that function).


## mohler/E03.Q01 (5 marks)

**Question:** What does a function signature include?

**Model answer:** The name of the function and the types of the parameters.

- **P1** (2.5): States that a function signature includes the name of the function (equivalent wording accepted).
- **P2** (2.5): States that a function signature includes the types of the parameters (equivalent wording accepted, e.g. parameter/argument types).


## mohler/E03.Q03 (5 marks)

**Question:** How does the compiler handle inline functions?

**Model answer:** It makes a copy of the function code in every place where a function call is made.

- **P1** (3): States that the compiler replaces/expands the inline function call with a copy of the function's code (body) at the point of the call (equivalent wording, e.g. 'substitutes the function body in place of the call', earns the mark).
- **P2** (2): States that this copying happens at every place where the function is called (each call site gets its own copy), rather than a single shared function that is jumped to.


## mohler/E03.Q04 (5 marks)

**Question:** What is the main advantage associated with function arguments that are passed by reference?

**Model answer:** It avoids making copies of large data structures when calling functions.

- **P1** (3): States that passing by reference avoids copying the argument (data) when the function is called, rather than passing a duplicate (equivalent wording such as 'no copy is made', 'passes the address/original instead of a copy').
- **P2** (2): Links this benefit to large data structures (e.g. big arrays, objects), i.e. saving memory/time/improving efficiency for large data.


## mohler/E03.Q06 (5 marks)

**Question:** When defining a recursive function, what are possible causes for infinite recursion?

**Model answer:** If the recursion step is defined incorrectly, or if the base case is not included.

- **P1** (2.5): States that a missing base case (no terminating condition) can cause infinite recursion. Equivalent wording accepted, e.g. 'no stopping condition', or a base case that is never reached.
- **P2** (2.5): States that an incorrectly defined recursion step can cause infinite recursion, e.g. the recursive call does not move toward the base case / does not reduce the problem. Equivalent wording accepted.


## mohler/E04.Q05 (5 marks)

**Question:** How many dimensions need to be specified when passing a multi-dimensional array as an argument to a function?

**Model answer:** All the dimensions, except the first one.

- **P1** (5): States that all dimensions except the first must be specified (the first dimension's size may be omitted). Equivalent wording, e.g. 'every dimension other than the first', or an example like int a[][10][20] for a 3D array, earns the marks. _Partial: Award 2.5 if the student says only that dimensions must be specified without correctly identifying that the first can be omitted (e.g. 'all dimensions'), or says the sizes of the later dimensions are needed but is vague about the first._


## mohler/E05.Q02 (5 marks)

**Question:** In one sentence, what is the main idea implemented by selection sort?

**Model answer:** Taking one array element at a time, from left to right, it identifies the minimum from the remaining elements and swaps it with the current element.

- **P1** (1.5): States that the algorithm processes the array one position/element at a time, from left to right (i.e., builds the sorted portion progressively from the left, position by position).
- **P2** (2): States that for the current position it finds/identifies the minimum element among the remaining (unsorted) elements.
- **P3** (1.5): States that this minimum is swapped with the element at the current position.


## mohler/E05.Q03 (5 marks)

**Question:** What is the number of operations for insertion sort under a best-case scenario, and what is the best-case scenario?

**Model answer:** N -LRB- the length of the array -RRB- operations achieved for a sorted array.

- **P1** (3): States that the best-case number of operations is N (linear, O(N)), where N is the length of the array. Equivalent wording such as 'n comparisons' or 'linear time' earns the marks.
- **P2** (2): States that the best case occurs when the array is already sorted (in the desired order). Equivalent wording earns the marks.


## mohler/E06.Q03 (5 marks)

**Question:** What does the star -LRB- STAR -RRB- operator return?

**Model answer:** An alias -LRB- synonym -RRB- for the name of the object that its operand points to in memory. It is the dereferencing operator.

- **P1** (3): States that the star (*) operator returns an alias/synonym for the name of the object (i.e. the object itself / the value stored at that location) that its operand points to in memory. Equivalent wording such as 'the value/object at the address the pointer points to' earns the marks.
- **P2** (2): Identifies the star operator as the dereferencing (indirection) operator.


## mohler/E06.Q05 (5 marks)

**Question:** What does the sizeof operator return?

**Model answer:** The size in bytes of its operand.

- **P1** (5): States that sizeof returns the size of its operand (a type or expression/variable) in bytes. Equivalent wording accepted (e.g. 'number of bytes occupied by a variable or data type'). _Partial: Award 2.5 if the answer says it returns the 'size' of the operand but does not mention bytes (or the unit), or mentions bytes but not that it relates to the operand._


## mohler/E08.Q01 (5 marks)

**Question:** What is a stack?

**Model answer:** A data structure that can store elements, which has the property that the last item added will be the first to be removed -LRB- or last-in-first-out -RRB-

- **P1** (1.5): States that a stack is a data structure (a collection that stores elements/items).
- **P2** (3.5): States that the last item added is the first to be removed (last-in-first-out / LIFO). Equivalent wording, e.g. 'most recently added element is removed first', earns the marks. _Partial: Award 2 marks if only the acronym LIFO is given with no explanation, or if the ordering is described imprecisely but is clearly last-in/first-out in intent._


## mohler/E09.Q06 (5 marks)

**Question:** What is the stack operation corresponding to the enqueue operation in queues?

**Model answer:** push

- **P1** (5): States that the stack operation corresponding to enqueue is push (equivalent wording such as 'push operation' or 'pushing onto the stack' is accepted).


## mohler/E11.Q07 (5 marks)

**Question:** What is the difference between an array that is declared as static and one that is not?

**Model answer:** The static arrays are intialized only once when the function is called.

- **P1** (2.5): States that a static array is initialized only once (e.g., at first call/program start) and is not re-initialized on each function call. Equivalent wording accepted.
- **P2** (2.5): Contrasts with a non-static (automatic/local) array, which is created and re-initialized every time the function is called (and does not keep its previous contents between calls).


## mohler/E11.Q09 (5 marks)

**Question:** Briefly describe the divide-and-conquer paradigm.

**Model answer:** Divide a problem into smaller subproblems, solve them recursively, and then combine the solutions into a solution for the original problem.

- **P1** (2): States that the problem is divided (broken down) into smaller subproblems (of the same type).
- **P2** (1.5): States that the subproblems are solved, recursively (equivalent: solved independently, with the same method applied to each, down to base cases).
- **P3** (1.5): States that the solutions to the subproblems are combined (merged) to form the solution to the original problem.


## mohler/E12.Q06 (5 marks)

**Question:** What is a queue?

**Model answer:** A data structure that stores elements following the first in first out principle. The main operations in a queue are enqueue and dequeue.

- **P1** (1): Identifies a queue as a data structure that stores a collection of elements.
- **P2** (2): States that it follows the first in first out (FIFO) principle, i.e. the element added first is removed first. Equivalent wording accepted.
- **P3** (2): Names the main operations: enqueue (add an element at the rear/back) and dequeue (remove an element from the front). _Partial: 1 mark for naming only one of enqueue or dequeue correctly._
