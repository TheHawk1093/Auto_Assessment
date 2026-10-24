# mohler: generated rubrics

Marks per point add up to the question total.

## mohler/E01.Q03 (5 marks)

**Question:** What are the main advantages associated with object-oriented programming?

**Model answer:** Abstraction and reusability.

- **P1** (2.5): States abstraction as an advantage of OOP (hiding complex implementation details and exposing only essential features). Equivalent wording accepted.
- **P2** (2.5): States reusability as an advantage of OOP (code or classes can be reused, e.g. through inheritance). Equivalent wording accepted.


## mohler/E01.Q05 (5 marks)

**Question:** What is a variable?

**Model answer:** A location in memory that can store a value.

- **P1** (2.5): States that a variable is a location in memory (a storage location / named memory space / container held in memory). Equivalent wording accepted. _Partial: Half marks (1.25) if it only says a 'container' or 'place' to hold data without any reference to memory/storage location._
- **P2** (2.5): States that it stores/holds a value (data) that can be used by the program. Equivalent wording accepted. _Partial: Half marks (1.25) if the value is implied but vague, e.g. 'used for data' without saying it stores or holds a value._


## mohler/E02.Q02 (5 marks)

**Question:** What is the difference between a data member and a local variable inside a member function?

**Model answer:** Data members can be accessed from any member functions inside the class defintion. Local variables can only be accessed inside the member function that defines them.

- **P1** (2): States that a data member can be accessed by any/all member functions of the class (class-wide scope).
- **P2** (2): States that a local variable can only be accessed inside the member function that defines it (function-limited scope).
- **P3** (1): Makes a clear contrast between the two, i.e. data member scope is the whole class while local variable scope is a single function. Equivalent wording accepted. _Partial: Half marks if the contrast is only implied by separate descriptions without explicit comparison._


## mohler/E03.Q01 (5 marks)

**Question:** What does a function signature include?

**Model answer:** The name of the function and the types of the parameters.

- **P1** (2.5): States that a function signature includes the name of the function (identifier). Equivalent wording accepted.
- **P2** (2.5): States that a function signature includes the parameters' types (the types of the parameters/arguments). Equivalent wording accepted. _Partial: Award half (1.25) if the student mentions parameters (e.g., number or names of parameters) but does not mention their types._


## mohler/E03.Q03 (5 marks)

**Question:** How does the compiler handle inline functions?

**Model answer:** It makes a copy of the function code in every place where a function call is made.

- **P1** (3): States that the compiler replaces/expands the inline function call with the function's code (the function body is substituted at the call site). Equivalent wording such as 'inline expansion' or 'code is pasted in place of the call' earns the mark. _Partial: Award 1.5 if the student only says the function is treated specially/inlined, or that the call is avoided, without clearly saying the code is inserted at the call._
- **P2** (2): States that this happens at every place/each point where the function is called (a separate copy of the code for each call). _Partial: Award 1 if the student implies copies are made but does not make clear it applies to every call site (e.g. says 'a copy is made' only once)._


## mohler/E03.Q04 (5 marks)

**Question:** What is the main advantage associated with function arguments that are passed by reference?

**Model answer:** It avoids making copies of large data structures when calling functions.

- **P1** (3): States that passing by reference avoids copying the argument/data when the function is called (no copy of the data is made; the function works on the original via a reference/address). _Partial: Award 1.5 if the student only says it passes the address/reference or allows the function to modify the original, without stating that copying is avoided._
- **P2** (2): Links the benefit to large data structures (e.g. big arrays, objects, structs), i.e. the saving matters when the data is large. _Partial: Award 1 if the student mentions efficiency (less memory/time) in general terms without referring to large data or the cost of copying._


## mohler/E03.Q06 (5 marks)

**Question:** When defining a recursive function, what are possible causes for infinite recursion?

**Model answer:** If the recursion step is defined incorrectly, or if the base case is not included.

- **P1** (2.5): States that infinite recursion can be caused by a missing base case (no terminating condition is included in the function), so the recursion never stops. _Partial: Award 1.25 if the student mentions a base/terminating condition but is vague about it being absent or not reached._
- **P2** (2.5): States that infinite recursion can be caused by an incorrectly defined recursion step (e.g. the recursive call does not move the argument toward the base case, so the base case is never reached). _Partial: Award 1.25 if the student says the recursive call/step is wrong but gives no indication that it fails to approach the base case._


## mohler/E04.Q05 (5 marks)

**Question:** How many dimensions need to be specified when passing a multi-dimensional array as an argument to a function?

**Model answer:** All the dimensions, except the first one.

- **P1** (3): States that all dimensions except the first must be specified (e.g. for a 2-D array, the number of columns must be given; for an n-D array, the sizes of dimensions 2 to n). _Partial: 1.5 marks if the answer says only that the dimensions other than one must be given, or gives a correct example without stating the general rule._
- **P2** (2): Identifies the first dimension as the one that may be omitted / left unspecified (e.g. arr[][5]). _Partial: 1 mark if the first dimension is mentioned as optional but the rest are not clearly stated as required._


## mohler/E05.Q02 (5 marks)

**Question:** In one sentence, what is the main idea implemented by selection sort?

**Model answer:** Taking one array element at a time, from left to right, it identifies the minimum from the remaining elements and swaps it with the current element.

- **P1** (1.5): States that the algorithm processes/moves through the array one element (position) at a time from left to right (growing a sorted prefix), i.e. the current element/position. _Partial: Half marks if only implies iterating through the array without the left-to-right/current-position idea._
- **P2** (2): States that for each current position it finds/identifies the minimum element among the remaining (unsorted) elements. _Partial: Half marks if it says it finds the minimum/smallest element but does not say it is from the remaining/unsorted part._
- **P3** (1.5): States that the minimum found is swapped with the current element (placed into the current position). _Partial: Half marks if it says the minimum is moved/placed in position but not that it is swapped with the current element._


## mohler/E05.Q03 (5 marks)

**Question:** What is the number of operations for insertion sort under a best-case scenario, and what is the best-case scenario?

**Model answer:** N -LRB- the length of the array -RRB- operations achieved for a sorted array.

- **P1** (2.5): States that the best-case number of operations for insertion sort is N (linear, O(N)), where N is the length of the array. Equivalent wording such as 'n comparisons' or 'linear time' is accepted. _Partial: Half marks if the answer gives a linear-type count but is imprecise (e.g. N-1 comparisons is fine for full marks; vague 'fast' or 'few operations' earns half)._
- **P2** (2.5): States that the best-case scenario is when the array is already sorted (in the desired order). _Partial: Half marks if the answer says the data is 'nearly sorted' or 'mostly in order' without saying already sorted._


## mohler/E06.Q03 (5 marks)

**Question:** What does the star -LRB- STAR -RRB- operator return?

**Model answer:** An alias -LRB- synonym -RRB- for the name of the object that its operand points to in memory. It is the dereferencing operator.

- **P1** (1.5): States that the star (*) operator is the dereferencing (indirection) operator. _Partial: Award 0.75 if only implied, e.g. says it 'accesses what a pointer points to' without naming it as dereferencing._
- **P2** (2): States that it returns/yields the object (value/variable) that its operand points to, i.e. the thing stored at the memory location the pointer holds. _Partial: Award 1 if it says it gives the value at the address but not that the operand is a pointer/points to memory._
- **P3** (1.5): States that the result is an alias (synonym) for the name of that object, i.e. it refers to the pointed-to object itself (can be used to read or modify it), not a copy or the address. _Partial: Award 0.75 if it says it can be used to access/modify the pointed-to object but does not use alias/synonym idea._


## mohler/E06.Q05 (5 marks)

**Question:** What does the sizeof operator return?

**Model answer:** The size in bytes of its operand.

- **P1** (2): States that sizeof returns a size (the amount of memory/storage occupied) of its operand, i.e. a size value rather than the operand's value. _Partial: Award 1 mark if the answer mentions memory/size vaguely (e.g. 'length' or 'space') without clearly tying it to the operand._
- **P2** (2): States that the size is measured in bytes (equivalent wording such as 'number of bytes' accepted).
- **P3** (1): Identifies that the size is that of the operand, which may be a variable, expression or data type (equivalent wording accepted).


## mohler/E08.Q01 (5 marks)

**Question:** What is a stack?

**Model answer:** A data structure that can store elements, which has the property that the last item added will be the first to be removed -LRB- or last-in-first-out -RRB-

- **P1** (1): States that a stack is a data structure (or abstract data type / collection).
- **P2** (1): States that it stores/holds a collection of elements (items).
- **P3** (3): States that the last item added is the first to be removed (LIFO behaviour); equivalent wording accepted. _Partial: 1.5 marks if LIFO is named only as an acronym or the ordering is stated vaguely or partly (e.g. 'items are added and removed from the top' without stating the last-in is first-out)._


## mohler/E09.Q06 (5 marks)

**Question:** What is the stack operation corresponding to the enqueue operation in queues?

**Model answer:** push

- **P1** (5): States that the stack operation corresponding to enqueue is push (equivalent wording such as 'push operation' or 'push()' accepted).


## mohler/E11.Q07 (5 marks)

**Question:** What is the difference between an array that is declared as static and one that is not?

**Model answer:** The static arrays are intialized only once when the function is called.

- **P1** (1.5): States that a static array is initialized only once (a single time), not on each function call. _Partial: Award 0.75 if only says it is initialized/allocated once without contrasting with non-static._
- **P2** (1.5): States that a static array retains/persists its contents (values) between function calls, i.e. its lifetime is the whole program run. _Partial: Award 0.75 for a vague statement such as 'it remembers/keeps its values' without mention of calls or lifetime._
- **P3** (1.5): States that a non-static (automatic/local) array is created and re-initialized every time the function is called, and its contents are lost when the function exits. _Partial: Award 0.75 if only one of: re-initialized each call, or destroyed/lost on exit._
- **P4** (0.5): Gives a supporting detail on storage or default behaviour, e.g. static array is stored in static/data memory (not the stack), is zero-initialized by default, or its scope remains local to the function while the lifetime is program-long; non-static array is on the stack with indeterminate values if uninitialized.


## mohler/E11.Q09 (5 marks)

**Question:** Briefly describe the divide-and-conquer paradigm.

**Model answer:** Divide a problem into smaller subproblems, solve them recursively, and then combine the solutions into a solution for the original problem.

- **P1** (2): States that the problem is divided (broken down) into smaller subproblems (of the same type/smaller instances).
- **P2** (1.5): States that the subproblems are solved, typically recursively (independently, until a base case/simple enough to solve directly). _Partial: Half marks (0.75) if says subproblems are solved but does not mention recursion or base cases._
- **P3** (1.5): States that the solutions to the subproblems are combined (merged) to form the solution to the original problem.


## mohler/E12.Q06 (5 marks)

**Question:** What is a queue?

**Model answer:** A data structure that stores elements following the first in first out principle. The main operations in a queue are enqueue and dequeue.

- **P1** (1): States that a queue is a data structure (a collection that stores elements).
- **P2** (2): States that it follows the First In First Out (FIFO) principle, i.e. the element added first is removed first. _Partial: 1 mark if FIFO is only named or only vaguely described (e.g. 'items leave in order') without clear explanation._
- **P3** (1): Names enqueue as a main operation (adds an element to the rear/end of the queue).
- **P4** (1): Names dequeue as a main operation (removes an element from the front of the queue).
