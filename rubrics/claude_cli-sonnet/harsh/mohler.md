# mohler: harsh rubrics

Marks per point add up to the question total.

## mohler/E01.Q01 (5 marks)

**Question:** What is the role of a prototype program in problem solving?

**Model answer:** To simulate the behaviour of portions of the desired software product.

_Marking stance: harsh. Full marks need the precise idea: a prototype simulates the behaviour of portions of the desired software product, with the word simulate (or exact equivalent) used. Part marks only when clearly more than half of a point is stated precisely. Vague statements (e.g. 'helps solve the problem', 'a test version') earn nothing, and wrong claims (e.g. that it is the final product) lose the affected point._

- **P1** (2.5): States that the prototype program's role is to simulate (imitate/model) the behaviour of the desired software product, using the term 'simulate' or 'simulation' (or an exact equivalent such as 'imitate the behaviour'). _Partial: Half marks if it says the prototype represents or models the software product but does not clearly say it simulates behaviour._
- **P2** (1.5): States that it simulates only portions/parts of the desired software product (a partial, not complete, version), not the whole system.
- **P3** (1): Correctly identifies what is simulated as the behaviour of the desired (final) software product, not just its appearance, code, or a finished product, and does not confuse the prototype with the final product or with a testing/debugging program.


## mohler/E01.Q02 (5 marks)

**Question:** What stages in the software life cycle are influenced by the testing stage?

**Model answer:** The testing stage can influence both the coding stage -LRB- phase 5 -RRB- and the solution refinement stage -LRB- phase 7 -RRB-

_Marking stance: harsh. Full marks require both stages named precisely: coding (phase 5) and solution refinement (phase 7). Naming only one earns at most its own point; vague talk about 'fixing bugs' without naming the stage earns nothing. Any wrong extra stage listed loses the final point, and an answer naming neither stage earns 0._

- **P1** (2): States that the testing stage influences the coding stage (phase 5). _Partial: Half credit if coding is identified but the phase is vaguely described (e.g. 'implementation' without naming coding) — only if clearly precise otherwise; otherwise none._
- **P2** (2): States that the testing stage influences the solution refinement stage (phase 7). _Partial: Half credit if refinement is identified but loosely worded (e.g. 'improving the solution') with the correct sense._
- **P3** (1): Gives exactly these two stages and no wrong extra stages (e.g. not design, requirements, maintenance, deployment as influenced stages).


## mohler/E01.Q03 (5 marks)

**Question:** What are the main advantages associated with object-oriented programming?

**Model answer:** Abstraction and reusability.

_Marking stance: harsh. Both advantages, abstraction and reusability, are required; each is worth half the marks and must be named precisely. Vague benefits (e.g. 'easier to code', 'organised', 'real-world modelling') earn nothing. A wrong claim about either point, or naming only one, loses the other point's marks as stated; a wrong extra advantage does not earn marks but a wrong statement about abstraction or reusability voids that point._

- **P1** (2.5): States abstraction as a main advantage of object-oriented programming (hiding implementation detail and exposing only essential features), using the term 'abstraction'. _Partial: Half marks if the idea of hiding details/showing only essentials is described precisely but the term 'abstraction' is not used._
- **P2** (2.5): States reusability as a main advantage of object-oriented programming (code/classes can be reused, e.g. via inheritance), using the term 'reusability' or 'reuse'. _Partial: Half marks if reuse of existing code/classes (e.g. via inheritance) is described precisely but the term 'reusability/reuse' is not used._


## mohler/E01.Q04 (5 marks)

**Question:** Where do C plus plus programs begin to execute?

**Model answer:** At the main function.

_Marking stance: harsh. Full marks need 'main' (the main function) named precisely as the place where execution begins. Give part marks only if main is named but the starting role is vague. Award 0 if the answer names a different place (first function, header file, constructor, #include) or does not name main._

- **P1** (4): States that execution of a C++ program begins at the main function, named explicitly as 'main' (main()). _Partial: 2 marks if main is named but the answer is vague about it being where execution starts (e.g. 'main is important' or 'in the program's first function' naming main only implicitly)._
- **P2** (1): Makes clear that main is the entry point, i.e. the point where execution starts, and not merely a function that is present in the program (e.g. not the first function written, a header, or a class/other function).


## mohler/E01.Q05 (5 marks)

**Question:** What is a variable?

**Model answer:** A location in memory that can store a value.

_Marking stance: harsh. Full marks need both parts stated precisely: a location in memory, and that it stores a value. Vague answers such as 'something that changes' or 'a name for data' earn nothing for the memory-location point. Wrong statements (e.g. a variable is a function or a constant value itself) lose the point they contradict._

- **P1** (2.5): States that a variable is a location in memory (a named memory location/storage location in RAM), using the term 'memory' and 'location' precisely. _Partial: Half marks if it says only 'a place to store data' or 'a named storage' without clearly stating it is a memory location._
- **P2** (2.5): States that this memory location stores/holds a value (data) that can be stored in it, i.e. the variable holds a value. _Partial: Half marks if it says it holds data but with a wrong or vague qualifier, e.g. 'stores information' without it being tied to the memory location._


## mohler/E01.Q06 (5 marks)

**Question:** Where are variables declared in a C plus plus program?

**Model answer:** Variables can be declared anywhere in a program. They can be declared inside a function -LRB- local variables -RRB- or outside the functions -LRB- global variables -RRB-

_Marking stance: harsh. Full marks need all three elements: declaration anywhere, inside functions as local variables, and outside functions as global variables, with the correct terms. Part marks only when clearly more than half of a point is precise. Vague answers (e.g. 'at the top') or any wrong statement about a point earn nothing for that point; a wrong location, such as 'only in main', loses the related point._

- **P1** (1.5): States that variables can be declared anywhere in a program (not restricted to one fixed location). _Partial: Half marks if only one location is given as an example without saying declaration is possible anywhere._
- **P2** (1.75): States precisely that variables can be declared inside a function, and names these as local variables. _Partial: Half marks if inside a function is stated but 'local variables' is not named (or vice versa)._
- **P3** (1.75): States precisely that variables can be declared outside all functions, and names these as global variables. _Partial: Half marks if outside functions is stated but 'global variables' is not named (or vice versa)._


## mohler/E01.Q07 (5 marks)

**Question:** What is the main difference between a while and a do ... while statement?

**Model answer:** The block inside a do ... while statement will execute at least once.

_Marking stance: harsh. Full marks need the precise fact that a do ... while body runs at least once, plus the contrast that a while body may run zero times because the condition is tested first. Vague wording such as 'they are different loops' or 'do while is more flexible' earns nothing. A wrong statement, for example saying while always runs once, loses the point it affects._

- **P1** (3): States that the block (body) of a do ... while statement always executes at least once. _Partial: Half credit if it says do...while runs the body before checking the condition but does not say 'at least once'._
- **P2** (2): Correctly contrasts with while: in a while loop the condition is tested before the body, so the block may execute zero times (not at all) if the condition is initially false. _Partial: Half credit if it only says while checks the condition first without stating the body may run zero times._


## mohler/E02.Q01 (5 marks)

**Question:** What is typically included in a class definition?

**Model answer:** Data members -LRB- attributes -RRB- and member functions.

_Marking stance: harsh. Full marks need both data members (attributes) and member functions (methods) named with correct terms. Give nothing for a point if it is vague (e.g. 'variables and code', 'stuff inside the class') or wrong. P3 is lost if the student adds a wrong item or mixes up the two. Naming only one of the two earns at most that one point's marks._

- **P1** (2): States that a class definition includes data members, using the term 'data members' or 'attributes' (member variables), i.e. the data/state of the class.
- **P2** (2): States that a class definition includes member functions (methods), i.e. the behaviour/operations of the class, using the term 'member functions' or 'methods'.
- **P3** (1): Gives both elements together as the contents of the class (data members AND member functions) with no wrong or irrelevant extra item presented as part of the definition, and no confusion between the two.


## mohler/E02.Q02 (5 marks)

**Question:** What is the difference between a data member and a local variable inside a member function?

**Model answer:** Data members can be accessed from any member functions inside the class defintion. Local variables can only be accessed inside the member function that defines them.

_Marking stance: harsh. Full marks need both scopes stated precisely: data members usable in any member function of the class, local variables only within the member function that declares them. Vague wording (e.g. 'data members are global', 'locals are temporary') earns nothing for that point, and a wrong claim about either scope voids that point. Mentioning only one side earns at most that side's marks and no contrast mark._

- **P1** (2): States that data members can be accessed from any member function of the class (scope is the whole class definition / all member functions). _Partial: 1 mark if only says data members are accessible in the class, without stating member functions (or 'any/all' member functions)._
- **P2** (2): States that local variables can be accessed only inside the one member function that defines them (scope limited to that function). _Partial: 1 mark if only says local variables are accessible only 'inside a function' without tying it to the function that defines them._
- **P3** (1): Gives a correct contrast between the two: data members are shared across all member functions of the class, whereas locals are confined to a single function, with both scopes stated together as a comparison.


## mohler/E02.Q03 (5 marks)

**Question:** What is the difference between a constructor and a function?

**Model answer:** A constructor is called whenever an object is created, whereas a function needs to be called explicitely. Constructors do not have return type, but functions have to indicate a return type.

_Marking stance: harsh. Full marks need both differences stated precisely as contrasts: automatic call on object creation vs explicit call for functions, and no return type for constructors vs a required return type for functions. Vague statements (e.g. "constructor initialises objects", "functions do tasks") earn nothing. Any wrong claim within a point, such as saying constructors return a value or have return type void, loses that point._

- **P1** (2.5): States that a constructor is called automatically/implicitly whenever an object is created (instantiated), whereas a function must be called explicitly by the programmer. _Partial: Half (1.25) if only one side is precise, e.g. constructor is called automatically on object creation but the explicit calling of functions is not stated._
- **P2** (2.5): States that a constructor has no return type (not even void), whereas a function must declare/indicate a return type. _Partial: Half (1.25) if only one side is stated precisely, e.g. constructors have no return type but the requirement for functions to declare one is missing._


## mohler/E02.Q04 (5 marks)

**Question:** When does C plus plus create a default constructor?

**Model answer:** If no constructor is provided, the compiler provides one by default. If a constructor is defined for a class, the compiler does not create a default constructor.

_Marking stance: harsh. Full marks need both facts stated precisely: the compiler supplies a default constructor when the class has no constructor, and it does not when any constructor is user-defined. Part marks only when clearly more than half of a point is stated. Vague statements, wrong claims (e.g. compiler always creates one, or the programmer creates it), or talk about unrelated constructor types earn nothing for that point._

- **P1** (2.5): States that the compiler (not the programmer) automatically provides/creates a default constructor when no constructor is defined/provided for the class. _Partial: Half marks if it says a default constructor is created automatically by the compiler but does not clearly state the condition that no constructor is provided._
- **P2** (2.5): States that if any constructor is defined for the class (e.g. a parameterized constructor), the compiler does NOT create a default constructor. _Partial: Half marks if it only implies this (e.g. 'only when no constructor exists') without explicitly stating that defining any constructor suppresses the implicit default constructor._


## mohler/E02.Q05 (5 marks)

**Question:** How many constructors can be created for a class?

**Model answer:** Unlimited number.

_Marking stance: harsh. Full marks need the precise claim that the number is unlimited (no fixed upper limit). Saying only 'many' or 'more than one' earns at most half of P1. Any specific finite number (e.g. one, two, three) or saying it is limited earns nothing for P1. P2 is only earned if overloading/different parameter lists is stated correctly; a wrong statement there earns nothing for P2._

- **P1** (3): States that a class can have an unlimited number of constructors (no fixed limit on how many can be created). _Partial: Half (1.5) if the student says 'many/multiple' constructors without stating there is no limit._
- **P2** (2): Correctly qualifies that the constructors are distinguished by differing parameter lists, i.e. constructor overloading (each must have a different signature). _Partial: Half (1) if overloading or differing parameters is mentioned only vaguely without the term 'overloading' or 'parameter list/signature'._


## mohler/E02.Q06 (5 marks)

**Question:** What is the difference between a function prototype and a function definition?

**Model answer:** A function prototype includes the function signature, i. e., the name of the function, the return type, and the parameters 's type. The function definition includes the actual body of the function.

_Marking stance: harsh. Full marks need the prototype stated as the signature (name, return type, parameter types) and the definition as containing the actual body, with a clear contrast. Give part marks on P1 only if two of the three signature elements are precise. Vague wording such as "prototype just declares it" without signature contents, or any wrong statement about a point, earns nothing for that point._

- **P1** (2): States that a function prototype (declaration) contains the function signature: the function name, the return type, and the parameter types (all three elements named). _Partial: 2 of 3 marks-worth only if clearly more than half: two of the three elements (name, return type, parameter types) stated precisely; award 1 mark._
- **P2** (2): States that the function definition contains the actual body of the function (the implementation/code executed when called).
- **P3** (1): Makes the distinction explicitly: the prototype gives only the signature without a body, whereas the definition supplies the body (signature plus implementation); the two are not conflated.


## mohler/E02.Q07 (5 marks)

**Question:** What is the role of a header-file?

**Model answer:** To store a class interface, including data members and member function prototypes.

_Marking stance: harsh. Full marks need the class interface stated precisely, plus both data members and member function prototypes named. Vague answers (e.g. 'stores code', 'for including libraries', 'organizes the program') earn nothing. Saying the header holds function implementations or definitions is a wrong statement, so the points it affects earn nothing._

- **P1** (2): States that a header file stores/contains the class interface (the class declaration), as opposed to the implementation (definitions of member functions), which belongs in the .cpp file. _Partial: Half marks (1) if it says it holds declarations/class definition generally but does not use the term interface or does not contrast it with the implementation file._
- **P2** (1.5): States that the class interface in the header includes the data members (member variable declarations).
- **P3** (1.5): States that the class interface in the header includes member function prototypes (declarations only, not function bodies).


## mohler/E03.Q01 (5 marks)

**Question:** What does a function signature include?

**Model answer:** The name of the function and the types of the parameters.

_Marking stance: harsh. Full marks need both the function name and the parameter types, stated precisely. Saying only 'parameters' without types earns at most half of P2; naming only one element earns just that point. Any wrong inclusion, such as the function body, loses P3, and vague statements like 'details about the function' earn nothing. A return type is not in the model answer, so mentioning it neither earns nor costs marks unless it replaces a required element._

- **P1** (1.5): States that a function signature includes the name of the function (the function name/identifier).
- **P2** (2.5): States that it includes the types of the parameters (the parameter type list, i.e. data types of the arguments), using correct terms such as 'parameter types'. _Partial: Half: mentions parameters but without their types (e.g. 'the parameters' or 'number of parameters' only)._
- **P3** (1): Gives both elements together as the signature's content, with no wrong extra element (e.g. does not claim the signature includes the function body or the parameter names as required parts).


## mohler/E03.Q02 (5 marks)

**Question:** What is the scope of global variables?

**Model answer:** File scope.

_Marking stance: harsh. Full marks only if the answer says file scope (accessible throughout the file/translation unit, declared outside any function). Part marks only for a precise partial statement, such as accessible to all functions without naming file scope. Wrong scopes (local, block, function scope) or vague answers such as 'global' or 'everywhere' earn nothing; stating a wrong scope alongside the right one also earns nothing._

- **P1** (5): States that global variables have file scope, i.e. they are declared outside all functions/blocks and are accessible from the point of declaration to the end of the file (translation unit), so usable by all functions in that file. _Partial: Award 2.5 only if the student gives clearly more than half of this precisely, e.g. says they are accessible by all functions in the program/file but does not use the term 'file scope'; vague answers such as 'everywhere' earn 0._


## mohler/E03.Q03 (5 marks)

**Question:** How does the compiler handle inline functions?

**Model answer:** It makes a copy of the function code in every place where a function call is made.

_Marking stance: harsh. Full marks need a precise statement that the compiler copies/expands the function code at every call site, and that this replaces the normal call. Vague wording such as "it makes it faster" or "it is treated specially" earns nothing. Any wrong statement (e.g. the function is called once and shared, or the copy is made at run time by the CPU) loses the point it affects._

- **P1** (2.5): States that the compiler makes/inserts a copy of the function's code (the function body is expanded in place; inline expansion) instead of a normal call. _Partial: Half: says the function body is substituted/expanded but does not clearly say a copy of the code is made._
- **P2** (1.5): States that this copy is placed at every place where the function is called (each call site), i.e. the call is replaced by the code. _Partial: Half: says code is inserted at the call but not that it happens at every call._
- **P3** (1): Correctly distinguishes from a normal function call: no jump/call to a single separate copy of the function is made at run time (the call is replaced rather than executed as a call).


## mohler/E03.Q04 (5 marks)

**Question:** What is the main advantage associated with function arguments that are passed by reference?

**Model answer:** It avoids making copies of large data structures when calling functions.

_Marking stance: harsh. Full marks need a precise statement that pass by reference avoids copying, that this matters for large data structures, and a correct contrast with pass by value. Vague claims like "it is faster" or "it is better" earn nothing alone. Stating that the main advantage is modifying the original, or any wrong statement about a point, loses that point._

- **P1** (2.5): States that passing by reference avoids making copies (of the arguments) when the function is called, i.e. the function works on the original rather than a copy. _Partial: Half marks if it says no copy is made / works on the original but does not tie it to the function call or arguments precisely._
- **P2** (1.5): Specifies that the saving matters for large data structures (e.g. large objects, arrays, structs), where copying would be costly in time/memory. _Partial: Half marks if it mentions efficiency or memory/time savings but does not name large data structures._
- **P3** (1): Correctly distinguishes from pass by value, where a copy of the argument is made on each call; and does not wrongly present the advantage as something else (e.g. only being able to modify the variable, or the reference being a copy).


## mohler/E03.Q05 (5 marks)

**Question:** How are overloaded functions differentiated by the compiler?

**Model answer:** Based on the function signature. When an overloaded function is called, the compiler will find the function whose signature is closest to the given function call.

_Marking stance: harsh. Full marks need both the term 'signature' (or precise parameter-list wording) and the closest-match selection at call time. Vague answers such as 'by the name' or 'by the compiler' earn nothing; saying differentiation is by return type or name alone is wrong and loses P1. Part marks only where clearly more than half of a point is precisely stated._

- **P1** (2.5): States that overloaded functions are differentiated by their function signature, i.e. the parameter list (number, types and/or order of parameters), using the term 'signature' or an explicit parameter-list equivalent. _Partial: Half: says differentiated by parameters (number or types) but does not use the term signature or name both number and type/order._
- **P2** (2.5): States that when an overloaded function is called, the compiler selects/finds the function whose signature is closest (best match) to the arguments given in the call. _Partial: Half: says the compiler matches the call to a function by its arguments but does not say best/closest match._


## mohler/E03.Q06 (5 marks)

**Question:** When defining a recursive function, what are possible causes for infinite recursion?

**Model answer:** If the recursion step is defined incorrectly, or if the base case is not included.

_Marking stance: harsh. Full marks need both causes stated precisely with correct terms: missing base case, and an incorrect recursion step (not progressing toward the base case). Each cause is worth half the marks; a vague or merely implied statement (e.g. 'the function keeps calling itself') earns nothing for that point. A wrong extra cause stated as a cause (e.g. 'too many variables') costs the point it conflicts with; answers giving only one cause get at most 2.5._

- **P1** (2.5): States that infinite recursion can be caused by a missing base case, i.e. the function has no terminating/base case condition that stops the recursive calls. _Partial: Half credit if a base case is mentioned but the statement is imprecise (e.g. says base case is wrong/never reached without saying it is missing)._
- **P2** (2.5): States that infinite recursion can be caused by an incorrectly defined recursion step, i.e. the recursive call does not move the argument/problem toward the base case. _Partial: Half credit if only says the recursive call is 'wrong' without stating that it fails to progress toward the base case._


## mohler/E03.Q07 (5 marks)

**Question:** What are the similarities between iteration and recursion?

**Model answer:** They both involve repetition; they both have termination tests; they can both occur infinitely.

_Marking stance: harsh. Full marks need all three similarities stated precisely: repetition, termination tests, and the possibility of infinite execution. Each point is earned only if clearly and correctly stated; vague or merely implied statements earn nothing. Any wrong claim about a point (e.g. saying recursion has no termination test) earns nothing for that point. Differences between the two earn no marks._

- **P1** (1.5): States that both iteration and recursion involve repetition (repeatedly executing a set of instructions/process), using this idea precisely.
- **P2** (2): States that both have termination tests (iteration has a loop-continuation test; recursion has a base case) and that each ends when its test is met. _Partial: 1 mark if says both terminate/end but does not identify a termination test (loop condition / base case) for both._
- **P3** (1.5): States that both can occur infinitely (iteration: infinite loop if the continuation test never becomes false; recursion: infinite recursion if the base case is never reached).


## mohler/E04.Q01 (5 marks)

**Question:** What are the two different ways of specifying the length of an array?

**Model answer:** In the array declaration, or by using an initializer list.

_Marking stance: harsh. Both ways are required: (1) size given in the array declaration and (2) size determined by an initializer list. Each way must be stated precisely; vague answers such as 'when creating it' or 'with values' earn nothing or at most half. Naming a wrong way (e.g. dynamic allocation with new, or sizeof) as one of the two costs that point._

- **P1** (2.5): States that the array length can be specified in the array declaration, i.e. explicitly giving the size in square brackets (e.g. int a[5];). _Partial: Half marks if only vaguely 'when declaring' without clearly saying the size is given in the declaration brackets._
- **P2** (2.5): States that the array length can be specified by using an initializer list, i.e. the size is deduced from the number of values in the braces (e.g. int a[] = {1,2,3};). _Partial: Half marks if it mentions initializing with values/braces but does not say the length comes from the initializer list._


## mohler/E04.Q02 (5 marks)

**Question:** What is the main difference between strings declared using the type string versus strings declared using an array of characters?

**Model answer:** The strings declared using an array of characters have a null element added at the end of the array.

_Marking stance: harsh. Full marks need the precise fact: a character-array string has a null character ('\0') appended as its final element, and the string type does not expose this. Vague answers (e.g. "arrays are fixed size", "string is easier to use") or any wrong claim, such as the string type having the null element, earn nothing for the affected point. Part marks only as stated in partial_credit._

- **P1** (3): States that strings declared as character arrays have a null element/null character ('\0', the null terminator) added at the end of the array. _Partial: Half (1.5): says character-array strings have an extra terminating/end marker element but does not name it as the null character '\0'._
- **P2** (2): Correctly contrasts with the string type: states that strings declared with type string do not have a null element added at the end of the array (the character-array form is the one with the null terminator).


## mohler/E04.Q03 (5 marks)

**Question:** How are arrays passed to functions?

**Model answer:** by reference.

_Marking stance: harsh. Full marks require the precise statement that arrays are passed by reference, plus the contrast with pass by value (no copy made, original array modified). Saying 'by value' or that a copy is made earns nothing for either point. Vague answers that merely mention functions or pointers without saying reference/original array earn nothing._

- **P1** (3): States that arrays are passed by reference (i.e., the function receives the array's address/reference to the original array, not a copy). _Partial: Award 1.5 if the student says the function works on/modifies the original array or passes the address but does not use the term 'by reference'._
- **P2** (2): Correctly distinguishes from pass by value: the array elements are not copied, so changes made inside the function affect the original array. _Partial: Award 1 if only says changes affect the original, without stating that no copy is made (or vice versa)._


## mohler/E04.Q04 (5 marks)

**Question:** What is the difference between an array declared as static, and one that is not?

**Model answer:** The arrays declared as static live throughout the life of the program; that is, they are initialized only once, when the function that declares the array it is first called.

_Marking stance: harsh. Full marks need precise statements: static array lives for the whole program, is initialized only once on the first call of its function, and the non-static array differs (re-created each call, destroyed on exit). Vague statements like 'static arrays keep their value' earn at most part of P1. Any wrong statement about a point (e.g. static arrays are re-initialized each call, or static means constant size) means that point earns nothing._

- **P1** (2): States that a static array persists (has static storage duration) for the entire life/lifetime of the program, rather than only during the function call, using terms such as 'static' and 'life of the program'. _Partial: 1 mark if it says static arrays persist/retain values between calls but does not state lifetime is the whole program._
- **P2** (2): States that a static array is initialized only once, the first time the function that declares it is called (not on each call). _Partial: 1 mark if it says initialized only once but omits that this happens at the first call of the declaring function._
- **P3** (1): Correctly contrasts with a non-static (automatic/local) array: it is created and initialized on each call of the function and destroyed when the function exits, so it does not live for the whole program.


## mohler/E04.Q05 (5 marks)

**Question:** How many dimensions need to be specified when passing a multi-dimensional array as an argument to a function?

**Model answer:** All the dimensions, except the first one.

_Marking stance: harsh. Full marks need the precise fact: every dimension except the first must be specified, with the first allowed to be left blank. Vague answers such as 'all dimensions', 'some dimensions' or 'the size' earn nothing for P1, and a wrong statement (e.g. 'only the first' or 'all dimensions') loses the point it concerns. Part marks only where clearly more than half of a point is stated precisely._

- **P1** (3): States that all dimensions except the first must be specified in the function's parameter (e.g. for a 3-D array, the 2nd and 3rd dimension sizes). _Partial: Half credit if the student says the dimensions other than the first (or 'all but one') must be given but does not clearly identify the first as the exception, or gives the right idea imprecisely._
- **P2** (1): Explicitly states that the first dimension may be omitted/left unspecified (e.g. int arr[][10]).
- **P3** (1): Gives a correct reason or distinction: the remaining (non-first) dimension sizes are needed by the compiler to compute element addresses/offsets, whereas the first dimension size is not needed for that calculation.


## mohler/E05.Q01 (5 marks)

**Question:** In one sentence, what is the main idea implemented by insertion sort?

**Model answer:** Taking one array element at a time, from left to right, it inserts it in the right position among the already sorted elements on its left.

_Marking stance: harsh. Full marks need all three elements stated precisely: one element at a time from left to right, inserted into its correct position, among the already sorted elements on its left. Part marks only if clearly more than half of a point is stated precisely. Vague descriptions such as 'it sorts by comparing elements', or confusing it with selection sort (picking the minimum) or bubble sort (swapping neighbours), earn nothing for the affected point._

- **P1** (1.5): States that insertion sort processes/takes one element at a time, moving from left to right through the array (the current element is taken in turn, with the elements to its left forming the already processed part). _Partial: Half: says one element at a time but omits left-to-right order (or vice versa)._
- **P2** (2): States that the taken element is inserted into its correct (right) position/place by comparing and shifting. _Partial: Half: says it is placed/moved but does not state it goes to its correct sorted position._
- **P3** (1.5): States that the insertion is among the already sorted elements on its left, i.e. the left part of the array is always sorted (sorted prefix/subarray), distinguishing it from selection sort or bubble sort (not selecting a minimum or swapping adjacent pairs repeatedly). _Partial: Half: mentions a sorted part but not that it is on the left, or says 'sorted elements' only vaguely._


## mohler/E05.Q02 (5 marks)

**Question:** In one sentence, what is the main idea implemented by selection sort?

**Model answer:** Taking one array element at a time, from left to right, it identifies the minimum from the remaining elements and swaps it with the current element.

_Marking stance: harsh. Full marks need all three elements stated precisely: left-to-right one element at a time, finding the minimum of the remaining elements, and swapping it with the current element. Vague wording such as "sorts by comparing elements" earns nothing. Wrong claims (e.g. adjacent swaps as in bubble sort, or inserting into a sorted part as in insertion sort, or picking the maximum) make the affected point earn nothing._

- **P1** (1.5): States that selection sort processes the array one element/position at a time from left to right (current position advances through the array, with the part before it being handled/sorted). _Partial: Half if it mentions going through elements one at a time but omits left-to-right order (or vice versa)._
- **P2** (2): States that for the current element it identifies/finds the minimum among the remaining (not yet processed) elements. _Partial: Half if it says it finds the minimum but does not specify that the search is over the remaining elements._
- **P3** (1.5): States that it swaps the found minimum with the current element (a swap, not shifting or inserting). _Partial: Half if it says the minimum is placed at the current position but does not say it is swapped._


## mohler/E05.Q03 (5 marks)

**Question:** What is the number of operations for insertion sort under a best-case scenario, and what is the best-case scenario?

**Model answer:** N -LRB- the length of the array -RRB- operations achieved for a sorted array.

_Marking stance: harsh. Full marks need both facts stated precisely: N (linear) operations, N being the array length, and the case being an already sorted array. Give part marks only where over half of a point is precise. A wrong complexity (e.g. N^2, log N) or a wrong scenario (e.g. reverse sorted, random) gets zero for that point. Vague answers such as "it is fast" earn nothing._

- **P1** (2): States that the best-case number of operations for insertion sort is N (linear, O(N)), where N is the length of the array. _Partial: 1 mark if says linear/O(N) or N but does not define N as the array length._
- **P2** (2): States that the best case occurs when the array is already sorted (in the desired order). _Partial: 1 mark if says nearly sorted or ordered without clearly stating already sorted._
- **P3** (1): Correctly links the two: only one comparison per element and no shifting is needed on a sorted array, hence N operations; distinguishes from worst case (reverse-sorted, N^2).


## mohler/E05.Q04 (5 marks)

**Question:** What is the base case for a recursive implementation of merge sort?

**Model answer:** When the size of the array to be sorted is 1 -LRB- or 2 -RRB-

_Marking stance: harsh. Full marks need the precise statement that recursion stops when the (sub)array has size 1 (or 2, per model answer), using terms like size/subarray and return. Part marks only if the size-1 condition is clearly given but loosely worded. Vague answers such as 'when it is divided enough' or 'when sorted', or any wrong size or wrong statement, earn nothing for the affected point._

- **P1** (3): States that the base case is reached when the (sub)array being sorted has size 1 (one element), i.e. it is already sorted, so the recursion stops and no further splitting occurs. Must refer to the size/length of the array or subarray being 1 (size 0 or 1 / 2 acceptable as the model's alternative). _Partial: Clearly gives the size condition (size 1) but without saying it is the subarray/stopping point of recursion, or only vaguely says 'small array'. Award 1.5._
- **P2** (1): Uses precise terminology: identifies the condition as the size (number of elements) of the array or subarray passed to the recursive call, e.g. 'if size == 1 (or low >= high) return', and that recursion stops/returns here rather than dividing or merging.
- **P3** (1): Gives no incorrect statement about the base case: does not claim the base case is when the array is sorted after merging, when the array is empty only, when the array is split in half, or any size other than 1 (or 2).


## mohler/E06.Q01 (5 marks)

**Question:** What is a pointer?

**Model answer:** A variable that contains the address in memory of another variable.

_Marking stance: harsh. Full marks need a precise statement that a pointer is a variable holding the memory address of another variable, using terms like "variable", "address" and "memory". Part marks only where clearly more than half of a point is precise, as stated in partial_credit. Vague answers such as "it points to something", "it is a reference" or "it is a data type", or any wrong statement (e.g. a pointer stores the value of another variable), earn nothing for that point._

- **P1** (2): States that a pointer is a variable (not merely an address, value or data type) that stores/holds/contains a memory address. _Partial: 1 mark if it says it stores an address but does not clearly call it a variable (or calls it a variable but is vague about what it holds)._
- **P2** (2): States that the address held is the memory location of another variable (i.e. the pointer refers to/points to another variable's location in memory). _Partial: 1 mark if it says it holds a memory address but does not say it is of another variable/object._
- **P3** (1): Correctly distinguishes a pointer from an ordinary variable: a pointer holds an address (indirect access to another variable), whereas an ordinary variable holds the data value itself.


## mohler/E06.Q02 (5 marks)

**Question:** What does the address -LRB- ADDRESS -RRB- operator return?

**Model answer:** The memory address of its operand.

_Marking stance: harsh. Full marks need a precise statement that & returns the memory address of its operand, with the address clearly distinguished from the operand's value. Part marks only if clearly more than half of a point is stated precisely, such as saying 'address' without 'memory' or the operand. Any wrong statement (e.g. says it returns the value) earns nothing for that point; generic or implied wording earns nothing._

- **P1** (3): States that the address-of operator (&) returns the memory address (location in memory) of its operand. 'Address' must be stated as a memory address; vague answers like 'a location' or 'the value' earn nothing. _Partial: Half (1.5) if it says it returns an address but not precisely that it is a memory address, or does not link it to the operand._
- **P2** (1): Makes clear the address returned is that of its operand (the variable/object the operator is applied to), e.g. &x gives the address of x, not x's value.
- **P3** (1): Correctly distinguishes it from the value: the result is the address where the operand is stored (a pointer value), not the contents/value of the operand (that is the dereference * operator).


## mohler/E06.Q03 (5 marks)

**Question:** What does the star -LRB- STAR -RRB- operator return?

**Model answer:** An alias -LRB- synonym -RRB- for the name of the object that its operand points to in memory. It is the dereferencing operator.

_Marking stance: harsh. Full marks need the precise fact: * returns an alias for the object its operand (a pointer) points to, and it is called the dereferencing operator. Vague wording such as "returns a value" or "something in memory" earns nothing on P1. Any wrong statement, such as saying it returns the address, loses the affected point._

- **P1** (2.5): States that the star (*) operator returns an alias (synonym) for the object/the name of the object that its operand points to in memory (i.e., the object at the address the pointer holds), stated precisely. _Partial: Half: says it returns the object/value the operand points to but does not mention alias/synonym for the object._
- **P2** (1): Names the operator correctly as the dereferencing (indirection) operator.
- **P3** (1.5): Correctly distinguishes it from the address-of operator (&) / from returning the pointer or address itself: the operand is a pointer and the result is the pointed-to object, not the address. _Partial: Half: states operand is a pointer/address and result is the object, without explicit contrast with the address or &._


## mohler/E06.Q04 (5 marks)

**Question:** How can an array be addressed in pointer or offset notation?

**Model answer:** By initializing a pointer to point to the first element of the array, and then incrementing this pointer with the index of the array element.

_Marking stance: harsh. Full marks need the precise two-part fact: a pointer set to the first element (base address), then offset by the index (e.g. *(p+i)). Vague statements such as "use pointers" earn nothing; give part marks only where clearly more than half of a point is stated precisely. A wrong statement on a point (e.g. pointer set to the last element) earns nothing for that point._

- **P1** (2): States that a pointer is initialized/set to point to the first element of the array (i.e., the array's base address, e.g. p = arr or p = &arr[0]). _Partial: 1 mark if a pointer to the array is mentioned but the first element/base address is not stated precisely._
- **P2** (2): States that the pointer is then incremented/offset by the index of the array element (e.g. *(p + i) or *(arr + i)) to reach that element. _Partial: 1 mark if offsetting/adding to the pointer is mentioned but the index as the offset is not stated precisely._
- **P3** (1): Makes clear that the offset (index) is added to the pointer and the result is dereferenced to access the element, distinct from subscript notation arr[i].


## mohler/E06.Q05 (5 marks)

**Question:** What does the sizeof operator return?

**Model answer:** The size in bytes of its operand.

_Marking stance: harsh. Full marks need the precise fact: sizeof gives the size in bytes of its operand, with 'bytes' and 'operand' (type or variable) clear. Vague answers such as 'the size' or 'memory used' earn no credit for the bytes point beyond the stated partial. Any wrong statement, such as saying it returns the value, the element count, or string length, loses the point it affects._

- **P1** (3): States that sizeof returns the size of its operand (a type or an expression/variable) measured in bytes, using the term 'bytes'. _Partial: Half (1.5) if it says it returns the size/memory taken by the operand but does not name bytes as the unit._
- **P2** (1): Makes clear the result is the size of the operand itself (a data type or a variable/object/expression), i.e. the memory occupied by that operand, not its value or its element count.
- **P3** (1): Correctly distinguishes it from related concepts: it returns a size (an unsigned integer value of type size_t), not the value stored in the operand, nor the number of elements or string length.


## mohler/E06.Q06 (5 marks)

**Question:** What are the different ways to pass a pointer to a function?

**Model answer:** There are four ways: nonconstant pointer to constant data, nonconstant pointer to nonconstant data, constant pointer to constant data, constant pointer to nonconstant data.

_Marking stance: harsh. Full marks need all four combinations named with correct pointer/data constness terminology, and the count of four. Part marks only where one of the two items in a point is precise. A vague answer (e.g. 'by value, by reference'), a swapped or wrong combination, or a wrong extra item earns nothing for the affected point._

- **P1** (1): States that there are four ways to pass a pointer to a function, and that these combine pointer constness (nonconstant/constant pointer) with data constness (constant/nonconstant data).
- **P2** (2): Names nonconstant pointer to constant data AND nonconstant pointer to nonconstant data precisely, with the terms 'constant' and 'nonconstant' applied correctly to pointer and data. _Partial: 1 mark if only one of the two is named precisely_
- **P3** (2): Names constant pointer to constant data AND constant pointer to nonconstant data precisely, with the terms 'constant' and 'nonconstant' applied correctly to pointer and data. _Partial: 1 mark if only one of the two is named precisely_


## mohler/E06.Q07 (5 marks)

**Question:** What is a function pointer?

**Model answer:** The address of the location in memory where the function code resides.

_Marking stance: harsh. Full marks need a precise statement that a function pointer holds the memory address where the function's code is located, using the terms address, memory and function code. Vague answers such as 'it points to a function' or 'it calls a function' earn nothing for P1 or P2 unless the address and memory location are stated. Any wrong claim, such as confusing it with a function that returns a pointer or with a data pointer, loses the affected point._

- **P1** (2): States that a function pointer is an address (a pointer holding the memory address) of the function. _Partial: 1 mark if it says it is a pointer/reference to a function but does not state that it holds an address_
- **P2** (2): States that the address is the location in memory where the function's code resides (the function's executable code/entry point in memory). _Partial: 1 mark if it mentions memory location but not that it is where the function code is stored_
- **P3** (1): Correctly distinguishes it from a pointer to data/variable or a function's return value: it points to function code, not to a data variable, and is not a function returning a pointer.


## mohler/E07.Q01 (5 marks)

**Question:** What is a linked list?

**Model answer:** A collection of elements that can be allocated dynamically.

_Marking stance: harsh. Full marks need all three: a collection of elements, dynamic allocation stated with the correct term, and a correct contrast with a fixed-size/static array. Vague answers such as "a list of data" or "elements connected together" earn nothing on P2 or P3. Any wrong statement within a point (e.g. saying elements are stored contiguously or the size is fixed) means that point earns zero._

- **P1** (2): States that a linked list is a collection of elements (nodes) — i.e. a data structure made up of a collection of elements. _Partial: Half marks if it says it is a data structure/list of items but does not state it is a collection of elements/nodes._
- **P2** (2): States that these elements can be allocated dynamically (memory allocated at run time, as needed, not fixed in size in advance). _Partial: Half marks if it says only that the size can grow/shrink without naming dynamic allocation._
- **P3** (1): Correctly distinguishes it from an array: elements are not required to be in contiguous/fixed-size static memory, since they are allocated dynamically.


## mohler/E07.Q02 (5 marks)

**Question:** What is the main advantage of linked lists over arrays?

**Model answer:** The linked lists can be of variable length.

_Marking stance: harsh. Full marks need the precise fact that linked lists have variable (dynamic) length, plus the contrast that arrays are fixed in size. Vague claims (e.g. 'more efficient', 'faster', 'uses less memory') earn nothing. Any wrong claim, such as linked lists having faster random access, removes the point it relates to._

- **P1** (3): States that linked lists can be of variable length, i.e. they can grow and shrink dynamically (size not fixed in advance), using precise terms such as 'variable length' / 'dynamic size'. _Partial: Half credit (1.5) if only a loosely related statement is given, e.g. 'flexible size' or 'no need to declare size' without saying length can change/vary._
- **P2** (2): Correctly contrasts with arrays: arrays have a fixed length (size fixed at declaration/creation), whereas linked lists do not.


## mohler/E07.Q03 (5 marks)

**Question:** What is the main advantage of arrays over linked lists?

**Model answer:** The elements in an array can be accessed directly -LRB- as opposed to linked lists, which require iterative traversal -RRB- .

_Marking stance: harsh. Full marks need the precise fact: arrays give direct (index-based) access, whereas linked lists need iterative traversal. Vague wording such as "arrays are faster" or "easier to use" earns nothing for that point. Naming a wrong advantage (e.g. easier insertion, dynamic size) as the main one loses P3 and likely P1._

- **P1** (2.5): States that array elements can be accessed directly (random/direct access by index, i.e. constant-time access to any element without traversing other elements). _Partial: Half if it says access is fast/by index but does not say it is direct or without traversal._
- **P2** (1.5): States that linked lists, by contrast, require iterative traversal (stepping node by node from the head) to reach an element. _Partial: Half if it only says linked lists are slower to access, without naming traversal._
- **P3** (1): Correctly makes the distinction in the right direction: the advantage is element access (direct vs sequential traversal), not insertion/deletion, memory use or size flexibility, and no wrong claim is made.


## mohler/E07.Q04 (5 marks)

**Question:** How are linked lists passed as arguments to a function?

**Model answer:** By reference.

_Marking stance: harsh. Full marks need the precise statement 'by reference' (reference/pointer to the head) plus the contrast with pass by value. Answers saying only 'by pointer' or vaguely 'using the head' earn at most part marks on P1. Saying 'by value' or any wrong statement about the passing method earns nothing on that point._

- **P1** (3): States that a linked list is passed to a function by reference (i.e., via a reference or pointer to the head node, so the function works on the original list rather than a copy), using the term 'by reference'. _Partial: Half: says the list is passed via a pointer to the head/head node but does not use the term 'by reference' or does not say it is the original list._
- **P2** (2): Correctly distinguishes this from pass by value: the list/head is not copied, so changes made inside the function (e.g., to the head or nodes) affect the original list. _Partial: Half: mentions only that changes persist or that no copy is made, without contrasting with pass by value._


## mohler/E07.Q05 (5 marks)

**Question:** What is the difference between a circular linked list and a basic linked list?

**Model answer:** The last element in a circular linked list points to the head of the list.

_Marking stance: harsh. Full marks need the precise fact: the last node of a circular list points to the head, and in a basic list the last node points to NULL. Vague statements such as "it goes in a circle" or "it is connected" earn nothing unless the last node and head are named. A wrong statement (e.g. the head points to the last node, or the basic list's last node points to the head) loses that point._

- **P1** (3): States that in a circular linked list the last element (last node) points back to the head (first node) of the list. _Partial: 1.5 if only says the list is circular/loops back without naming the last node pointing to the head/first node_
- **P2** (2): Contrasts with a basic (singly) linked list: the last node points to NULL (null/nullptr), so the list ends there and does not link back to the head. _Partial: 1 if only says the basic list has an end, without stating that the last node points to NULL_


## mohler/E07.Q06 (5 marks)

**Question:** What is the main advantage of a doubly-linked list over a basic linked list?

**Model answer:** All the deletion and insertion operations can be performed in constant time, including those operations performed before a given location in the list or at the end of the list.

_Marking stance: harsh. Full marks need constant time (O(1)) for insertion and deletion stated explicitly, including before a given location and at the end of the list, with the contrast to a basic list needing traversal. Vague answers such as "can move both directions" or "more flexible" earn nothing unless tied to constant-time operations. A wrong claim (e.g., faster search or less memory) loses the point it affects._

- **P1** (2): States that in a doubly-linked list insertion and deletion operations can be performed in constant time, O(1). _Partial: Half (1 mark) if says insertion/deletion is efficient or fast but does not state constant time/O(1), or gives constant time for only one of insertion or deletion._
- **P2** (1.5): States that this constant time holds for operations before a given location (at the node preceding a given position), because each node has a pointer to its previous node so no traversal from the head is needed. _Partial: Half (0.75) if mentions previous pointers/backward traversal but does not link it to constant-time operations before a given location._
- **P3** (1.5): States that constant-time operations also hold at the end of the list (e.g., deleting/inserting at the tail), whereas in a basic singly-linked list these require traversal (linear time) to find the preceding node. _Partial: Half (0.75) if mentions the end of the list but does not contrast with singly-linked list needing linear traversal, or vice versa._


## mohler/E07.Q07 (5 marks)

**Question:** What is the main disadvantage of a doubly-linked list over a basic linked list?

**Model answer:** Extra space required to store the back pointers.

_Marking stance: harsh. Full marks need both: extra space/memory as the disadvantage, and the cause stated precisely as the additional back (previous) pointer per node versus one pointer in a singly linked list. Vague answers such as "more complex" or "slower" earn nothing. A wrong claim, such as saying it is slower to traverse as the main disadvantage, loses the point it affects._

- **P1** (3): States that the disadvantage is extra memory/space: each node of a doubly-linked list must store an additional pointer (the back/previous pointer) in addition to the next pointer. _Partial: Half (1.5): says it uses more memory/space but does not identify the extra pointer per node as the cause._
- **P2** (2): Identifies the extra space specifically as the back (previous) pointer stored in every node, i.e. two pointers per node versus one in a basic (singly) linked list. _Partial: Half (1): mentions extra pointers but does not say back/previous or does not contrast with the single pointer in a basic list._


## mohler/E08.Q01 (5 marks)

**Question:** What is a stack?

**Model answer:** A data structure that can store elements, which has the property that the last item added will be the first to be removed -LRB- or last-in-first-out -RRB-

_Marking stance: harsh. Full marks need a data structure storing elements plus an exact statement of last-in-first-out removal order, with the LIFO idea clearly distinguished from a queue's FIFO. Vague descriptions (e.g., 'a pile of things', 'stores data') or any wrong order (FIFO) earn nothing for that point. Part marks only where clearly more than half of a point is precisely stated._

- **P1** (1): States that a stack is a data structure that stores elements (a collection of items).
- **P2** (2.5): States the LIFO property precisely: the last item added (pushed) is the first item removed (popped), using the term last-in-first-out (LIFO) or equivalent exact wording. _Partial: Half: describes removal order only roughly (e.g., 'last in comes out first' without naming LIFO or stating removal) but is clearly correct._
- **P3** (1.5): Correctly distinguishes a stack from a queue: a stack removes the most recently added item (LIFO), unlike a queue, which removes the earliest added item (FIFO); no wrong claim about order. _Partial: Half: implies the contrast correctly (e.g., mentions removal only from the top/most recent end) without explicitly naming the queue/FIFO contrast._


## mohler/E08.Q02 (5 marks)

**Question:** What are the two main functions defined by a stack?

**Model answer:** push and pop

_Marking stance: harsh. Full marks only if both named functions, push and pop, are given using these exact terms. Each function is worth its own half; naming only one earns that half only. Vague descriptions without the terms (e.g. "add and remove", "insert and delete") earn nothing, and a wrong extra function (e.g. peek, top, enqueue, dequeue) listed as a main function costs the whole answer's affected point._

- **P1** (2.5): States that push is one of the two main stack functions (operation that adds/inserts an element onto the top of the stack).
- **P2** (2.5): States that pop is the other main stack function (operation that removes an element from the top of the stack).


## mohler/E08.Q03 (5 marks)

**Question:** How can you implement a stack with an array?

**Model answer:** Keep the top of the stack toward the end of the array, so the push and pop operations will add or remove elements from the right side of the array.

_Marking stance: harsh. Full marks need the top of the stack placed at the end (right side) of the array, with push and pop both explicitly adding/removing at that end. Part marks only where clearly more than half of a point is stated precisely. Vague answers (e.g. "use an array with push and pop"), or putting the top at the front/left, earn nothing for that point._

- **P1** (2.5): States that the top of the stack is kept toward the end of the array (the right side / highest used index), not the front. _Partial: Half if it says the end/right side of the array is used but does not explicitly identify it as the top of the stack._
- **P2** (1.5): States that push adds an element and pop removes an element at that end, i.e. the right side of the array, so both operations act at the same end. _Partial: Half if only one of push or pop is correctly tied to the right/end side._
- **P3** (1): Gives the correct distinction: operations happen at the end (right side), not at the beginning (left side) of the array, so no elements need to be shifted.


## mohler/E08.Q04 (5 marks)

**Question:** How can you implement a stack with a list?

**Model answer:** Keep the top of the stack pointing to the head of the linked list, so the push and pop operations will add or remove elements at the beginning of the list.

_Marking stance: harsh. Full marks need the top pointing to the head of the linked list AND push and pop both acting at the beginning of the list, stated precisely with terms like head/top/push/pop. Vague answers ("use a list and add and remove elements") earn nothing. Any statement placing the top or the operations at the tail/end of the list, or an array-based answer, earns no marks for that point._

- **P1** (2.5): States that the top of the stack is kept pointing to the head (first node) of the linked list. _Partial: Half marks if the answer says a linked list is used and the top is at one end, but does not name the head/beginning precisely._
- **P2** (1.5): States that push adds an element at the beginning (head) of the list and pop removes the element at the beginning (head) of the list. Both operations must be stated. _Partial: Half marks if only one of push or pop is correctly stated at the beginning/head._
- **P3** (1): Makes clear that all stack operations therefore occur at the same end (the head), i.e. the top of the stack always corresponds to the head, not the tail/end of the list.


## mohler/E08.Q06 (5 marks)

**Question:** How are infix expressions evaluated by computers?

**Model answer:** First, they are converted into postfix form, followed by an evaluation of the postfix expression.

_Marking stance: harsh. Full marks need both stages stated precisely: infix converted to postfix first, then the postfix expression evaluated. Part marks only when clearly more than half of a point is stated. Answers that only describe infix, operator precedence or stacks generally, without naming postfix conversion, earn nothing. A wrong claim (e.g. converting to prefix or evaluating infix directly) loses the affected point._

- **P1** (2.5): States that the infix expression is first converted (transformed) into postfix form (postfix notation / reverse Polish notation). _Partial: Half if postfix is named as involved but the conversion step or its order (first) is not stated precisely._
- **P2** (1.5): States that the resulting postfix expression is then evaluated (e.g. by scanning it, typically using a stack) as the second step. _Partial: Half if evaluation is mentioned but not clearly of the postfix expression or not clearly as a second step._
- **P3** (1): Gives the correct two-stage order: conversion to postfix first, then evaluation of the postfix expression, rather than evaluating the infix expression directly.


## mohler/E08.Q07 (5 marks)

**Question:** What operations would you need to perform to find a given element on a stack?

**Model answer:** Pop all the elements and store them on another stack until the element is found, then push back all the elements on the original stack.

_Marking stance: harsh. Full marks need the precise operations named: pop to a second stack until the element is found, then push everything back onto the original stack. Part marks only when clearly more than half of a point is stated precisely. Vague answers (e.g. "traverse the stack", "search through it"), use of an array/queue instead of a stack, or wrong operations earn nothing for that point._

- **P1** (2): States that elements are popped from the original stack and stored/pushed onto another (auxiliary) stack, one by one, while searching (checking each popped element against the target). _Partial: Half (1 mark) if pop is stated but the second/temporary stack is not mentioned, or another stack is used without saying elements are popped one at a time while checking._
- **P2** (1): States that this popping continues until the required element is found (search stops at the target).
- **P3** (2): States that after the element is found, all the elements from the other stack are pushed back onto the original stack, restoring its original order/contents. _Partial: Half (1 mark) if push back is mentioned but the destination (original stack) or restoration is unclear._


## mohler/E09.Q01 (5 marks)

**Question:** What is a queue?

**Model answer:** A data structure that can store elements, which has the property that the last item added will be the last to be removed -LRB- or first-in-first-out -RRB- .

_Marking stance: harsh. Full marks need both: queue named as a data structure storing elements, and the exact first-in-first-out property. Give part marks only for a correct but loosely worded ordering. Give nothing for P2 if the answer says last-in-first-out, describes a stack, or contradicts FIFO. Vague statements like 'a line of things' earn nothing._

- **P1** (1): States that a queue is a data structure that stores elements (a collection/container of items).
- **P2** (4): States the ordering property precisely: first-in-first-out (FIFO), i.e. the first item added is the first removed, and the last item added is the last removed. The term FIFO or an equivalent exact statement of this order must be given. _Partial: 2 marks if the order is described correctly but only loosely (e.g. 'items are removed in the order added') without FIFO or first/last wording._


## mohler/E09.Q02 (5 marks)

**Question:** What are the two main functions defined by a queue?

**Model answer:** enqueue and dequeue

_Marking stance: harsh. Full marks require both exact terms, enqueue and dequeue, each with no wrong statement about it. Naming a term with a correct description of adding at the rear or removing from the front earns that point. Wrong or substituted names (push, pop, peek, insert, delete) or a wrong extra function earn nothing for the affected point; vague answers like 'add and remove' earn nothing unless the correct end is precisely stated._

- **P1** (2.5): States that enqueue is one of the two main queue functions: the operation that adds an element to the rear/back of the queue (the term 'enqueue' must be used). _Partial: Half marks if the operation is described correctly as adding at the rear but the term 'enqueue' is not named (or the term is named without a clear description) only if clearly more than half is precise; otherwise 0._
- **P2** (2.5): States that dequeue is the other main queue function: the operation that removes an element from the front of the queue (the term 'dequeue' must be used). _Partial: Half marks if removal from the front is described correctly but the term 'dequeue' is not named (or the term is named without a clear description) only if clearly more than half is precise; otherwise 0._


## mohler/E09.Q03 (5 marks)

**Question:** How can you implement a queue with an array?

**Model answer:** Use a circular array. Keep the rear of the queue toward the end of the array, and the front toward the beginning, and allow the rear pointer to wrap around.

_Marking stance: harsh. Full marks need all three elements stated precisely: circular array, front at beginning and rear at end, and the rear pointer wrapping around. Vague answers such as 'use an array with front and rear' earn nothing for the circular/wrap points. Wrong statements (e.g. front at end, shifting all elements on dequeue as the method) earn nothing for that point._

- **P1** (2): States that the queue is implemented using a circular array (circular/ring buffer arrangement of the array). _Partial: 1 mark if it describes the array being reused cyclically but does not use the term 'circular'; otherwise none._
- **P2** (1.5): States that the rear of the queue is kept toward the end of the array and the front toward the beginning of the array. _Partial: 0.75 if only one of front (beginning) or rear (end) is placed correctly._
- **P3** (1.5): States that the rear pointer (index) is allowed to wrap around from the end of the array back to the beginning. _Partial: 0.75 if wrapping is mentioned but not clearly attributed to the rear pointer or the end-to-beginning direction._


## mohler/E09.Q04 (5 marks)

**Question:** How can you implement a queue with a list?

**Model answer:** Keep the rear of the queue pointing to the tail of the linked list, so the enqueue operation is done at the end of the list, and keep the front of the queue pointing to the head of the linked list, so the dequeue operation is done at the beginning of the list.

_Marking stance: harsh. Full marks need both ends stated precisely: rear↔tail↔enqueue at end, and front↔head↔dequeue at beginning, using correct terms. Part marks only when clearly more than half of P1 or P2 is stated precisely. Vague answers ("use a linked list", "add and remove nodes") earn nothing, and any reversed pairing (e.g. enqueue at head) loses the affected points and P3._

- **P1** (2): States that the rear of the queue points to the tail of the linked list, so enqueue is done at the end (tail) of the list. _Partial: Half: names enqueue at the end/tail but does not link it to the rear pointer (or vice versa)._
- **P2** (2): States that the front of the queue points to the head of the linked list, so dequeue is done at the beginning (head) of the list. _Partial: Half: names dequeue at the beginning/head but does not link it to the front pointer (or vice versa)._
- **P3** (1): Gets the pairing right and distinct from the reverse: enqueue at tail/rear and dequeue at head/front, using the terms front, rear, head, tail, enqueue and dequeue correctly, with no swapped or contradictory statements.


## mohler/E09.Q06 (5 marks)

**Question:** What is the stack operation corresponding to the enqueue operation in queues?

**Model answer:** push

_Marking stance: harsh. Full 5 marks only if the student names "push" as the stack operation. Any other operation (e.g. pop, peek, dequeue, insert) or a vague description without the term "push" earns 0. A wrong extra operation offered alongside push (e.g. "push or pop") also earns 0._

- **P1** (5): States that the stack operation corresponding to enqueue is "push" (the exact term push; adding an element to the top of the stack).


## mohler/E10.Q01 (5 marks)

**Question:** What is a tree?

**Model answer:** A collection of nodes, which has a special node called root, and the rest of the nodes are partitioned into one or more disjoint sets, each set being a tree.

_Marking stance: harsh. Full marks need the precise recursive definition: a collection of nodes, one special node called the root, and the remaining nodes partitioned into one or more disjoint sets each of which is a tree. Generic statements (e.g. 'hierarchical structure', 'nodes connected by edges', 'parent and children') without these elements earn nothing for the matching point. Part marks only on P3 as stated; a wrong statement about a point (e.g. allowing cycles or multiple roots) loses that point._

- **P1** (1.5): States that a tree is a collection of nodes (a non-empty set of nodes), using the term 'nodes'.
- **P2** (1.5): States that the collection has one special node called the root.
- **P3** (2): States that the remaining nodes (other than the root) are partitioned into one or more disjoint sets, with the term 'disjoint' (non-overlapping) used, and each such set is itself a tree (recursive definition, i.e. subtrees). _Partial: 1 mark if clearly states the rest of the nodes are split into disjoint sets/subtrees but omits that each set is itself a tree (or the reverse)_


## mohler/E10.Q02 (5 marks)

**Question:** What is the height of a tree?

**Model answer:** The length of the longest path from the root to any of its leaves.

_Marking stance: harsh. Full marks need the precise statement: height = length of the longest path from the root to a leaf, using the terms 'longest', 'root' and 'leaf'. Part marks only where clearly more than half of a point is stated precisely. Vague answers (e.g. 'how tall the tree is', 'number of levels' without longest path, 'number of nodes') earn nothing, and a wrong statement (shortest path, or confusing with depth or size) loses that point._

- **P1** (2): States that height is the length of the longest path (the maximum number of edges/levels along a path) in the tree, i.e. the maximum over all paths, not just any path. _Partial: 1 mark if 'longest/maximum path' is stated but length is not made explicit, or length is given but 'longest' is imprecise_
- **P2** (2): States that the path runs from the root down to a leaf (a node with no children), using the terms 'root' and 'leaf'. _Partial: 1 mark if only one endpoint (root or leaf) is named correctly_
- **P3** (1): Correctly distinguishes height from depth: height is measured from the root to the deepest leaf for the whole tree, not the depth/level of a single arbitrary node, and not the number of nodes in the tree.


## mohler/E10.Q03 (5 marks)

**Question:** What is a leaf?

**Model answer:** A node that has no children.

_Marking stance: harsh. Full marks need the precise statement that a leaf is a node with no children, using correct terms. Vague phrasing such as 'the end of the tree' or 'last element' earns nothing for that point. Any wrong claim (e.g., a leaf has one child, or a leaf is the root only) removes the point it affects. The distinction point needs an explicit contrast with internal nodes._

- **P1** (3): States that a leaf is a node (of a tree) that has no children, using the term 'node' and 'no children' (or equivalently 'zero child nodes'/'no descendants'). _Partial: 1.5 if only 'a node at the end/bottom of the tree' or 'node with no children' without clearly identifying it as a node of a tree; otherwise none_
- **P2** (1): Precise terminology: identifies the leaf as a node in a tree (tree/binary tree context) and states its degree is zero / both child pointers are null (not merely 'last element' or 'end').
- **P3** (1): Correct distinction from related nodes: a leaf differs from an internal node (a node with at least one child) and from the root; a leaf is not defined by being the last-inserted or rightmost node.


## mohler/E10.Q04 (5 marks)

**Question:** What is a binary tree?

**Model answer:** A tree for which the maximum number of children per node is two.

_Marking stance: harsh. Full marks need a precise statement: a tree where every node has at most (maximum) two children, using the terms node and children. Vague wording such as 'a tree with two branches' or saying 'exactly two' children earns nothing for the relevant points. Descriptions of unrelated structures (e.g. BST ordering, heaps) without the core fact earn 0._

- **P1** (3): States that a binary tree is a tree (hierarchical structure of nodes) in which each node has a maximum of two children. _Partial: Half (1.5): says each node has two children or 'at most two' but does not identify it as a tree/node-based structure, or vice versa, stated precisely._
- **P2** (1): Uses the precise limit 'at most / maximum of two' children per node (i.e. 0, 1 or 2 children allowed), not 'exactly two'.
- **P3** (1): Uses the correct terms 'node' and 'children' (or left child and right child) when describing the restriction, applied per node.


## mohler/E10.Q05 (5 marks)

**Question:** What is a binary search tree?

**Model answer:** A binary tree that has the property that for any node the left child is smaller than the parent which in turn is smaller than the right child.

_Marking stance: harsh. Full marks need all three elements stated precisely: binary tree, left smaller than parent, parent smaller than right, applying to any node. A vague statement such as 'a sorted tree' or 'used for searching' earns nothing. A wrong ordering (e.g. left larger than parent) loses the point it affects, and confusing it with a plain binary tree or heap earns nothing for the property points._

- **P1** (1.5): States that a binary search tree is a binary tree (each node has at most two children, left and right). _Partial: Half credit if it says 'tree' with two children but does not use the term binary tree precisely._
- **P2** (1.75): States the ordering property precisely: for any node, the left child (left subtree) is smaller than the parent. _Partial: Half credit if the property is stated only loosely, e.g. 'left is smaller' without relating it to the parent node._
- **P3** (1.75): States the ordering property precisely: the parent is smaller than the right child (right subtree), i.e. left < parent < right, holding for every node. _Partial: Half credit if only the right-side relation is given without saying it applies to every node._


## mohler/E10.Q06 (5 marks)

**Question:** What is the inorder traversal of a binary tree?

**Model answer:** Traverse the left subtree, then the root, then the right subtree.

_Marking stance: harsh. Full marks need the exact order left subtree, root, right subtree with correct terms; vague wording like 'left, middle, right' loses most of P1. Any wrong order (e.g. root first or right before left) earns nothing for P1 and P3. Recursion and the contrast with preorder/postorder must be stated explicitly; merely implied statements earn nothing._

- **P1** (3): States the correct inorder order: left subtree first, then the root (node), then the right subtree, using these terms (left subtree, root, right subtree) in this order. _Partial: Half (1.5) if the order is clearly given but a required term is imprecise (e.g. 'left, middle, right' or 'left child' instead of subtree), or if only two of the three steps are in the correct order._
- **P2** (1): States that the traversal is applied recursively to each subtree (each subtree is itself traversed inorder), or equivalently that it is a depth-first traversal.
- **P3** (1): Correctly distinguishes inorder from preorder (root first) and postorder (root last), i.e. the root is visited between the left and right subtrees, not before or after both.


## mohler/E10.Q07 (5 marks)

**Question:** How many comparisons does it take to find an element in a binary search tree?

**Model answer:** The height of the tree -LRB- or log of the number of elements in the tree -RRB- .

_Marking stance: harsh. Full marks need both the precise term 'height' of the tree and the logarithm of the number of elements (log n). Part marks only when clearly more than half of a point is stated precisely. Answers like 'a few comparisons', 'n comparisons', or linear/total number of nodes earn nothing for the points they contradict; a wrong statement on a point voids that point._

- **P1** (3): States that the number of comparisons needed is equal to (at most) the height of the tree, using the term 'height' (or depth of the deepest path/levels from root to leaf). _Partial: Half (1.5) if it gives the number of levels/depth along a root-to-node path but does not use 'height' or say it is bounded by the height._
- **P2** (2): States the equivalent logarithmic form: the number of comparisons is about log (base 2) of the number of elements n, i.e. O(log n), for a balanced tree. _Partial: Half (1) if it says 'logarithmic' or O(log n) without relating it to the number of elements n or without stating it as the tree's height._


## mohler/E11.Q01 (5 marks)

**Question:** What are the elements typically included in a class definition?

**Model answer:** Function members and data members.

_Marking stance: harsh. Full marks need both elements named precisely: data members and function members (member functions/methods acceptable). Naming only one earns that point's marks only. Vague answers such as 'variables and stuff', or listing wrong extra items such as constructors only, or unrelated things like objects or headers as required elements, lose the affected point._

- **P1** (2.5): States that a class definition includes data members (member variables/attributes that hold the object's data), using the term 'data members' or an exact equivalent such as member variables. _Partial: Half credit if data members are described correctly but the term is imprecise (e.g. just 'variables') and the meaning is clearly right._
- **P2** (2.5): States that a class definition includes function members (member functions/methods that operate on the data), using the term 'function members' or an exact equivalent such as member functions or methods. _Partial: Half credit if function members are described correctly but the term is imprecise (e.g. just 'functions') and the meaning is clearly right._


## mohler/E11.Q02 (5 marks)

**Question:** What are the access-specifiers that can be used in a C plus plus class definition?

**Model answer:** Private and public.

_Marking stance: harsh. Full marks need both 'private' and 'public' named with the exact C++ keywords, and no incorrect extra specifier. Each missing or misnamed keyword loses that point; a vague description such as 'hidden' or 'open to all' without the term earns nothing. P3 is lost if any wrong item is listed as an access specifier. Naming 'protected' is not in the model answer, so treat it as an extra item and do not award P3 for it._

- **P1** (2): States that 'private' is an access specifier usable in a C++ class definition.
- **P2** (2): States that 'public' is an access specifier usable in a C++ class definition.
- **P3** (1): Gives only the specifiers private and public, with no wrong extra item presented as an access specifier (e.g. 'static', 'friend', 'internal').


## mohler/E11.Q03 (5 marks)

**Question:** How are objects initialized when they are created?

**Model answer:** By using constructors.

_Marking stance: harsh. Full marks need the precise term "constructor" as the means of initialization, plus the statement that it runs automatically when the object is created. Answers that only say "by initializing values", "by assignment" or name init functions, or that name something else such as a destructor, earn nothing for P1. Saying a wrong thing (e.g. initialization by destructor or by copy only) loses the point._

- **P1** (3.5): States that objects are initialized by constructors (a constructor, the special member function of the class), using the term 'constructor'. _Partial: Award 1.75 if it clearly names a special member function called when the object is created but does not use the term 'constructor' precisely._
- **P2** (1.5): States that the constructor is invoked automatically at the time the object is created.


## mohler/E11.Q04 (5 marks)

**Question:** What is a function signature?

**Model answer:** The name of the function and the list of parameters, including their types.

_Marking stance: harsh. Full marks only if the answer precisely says the signature is the function name plus the parameter list with parameter types. Each element is separate; vague wording such as "the function's details" or "how it is declared" earns nothing. A wrong statement about an element (e.g. saying the signature includes the function body, or that the return type is required) means that point earns nothing._

- **P1** (1.5): States that a function signature includes the name of the function (function name/identifier).
- **P2** (1.5): States that it includes the parameter list (the parameters the function takes).
- **P3** (2): States that the parameter list includes the types of the parameters (e.g. int, double), not just names or count.


## mohler/E11.Q05 (5 marks)

**Question:** What is a recursive function?

**Model answer:** A function that calls itself.

_Marking stance: harsh. Full marks need a precise statement that the function calls itself, from within its own body, with a correct contrast to loops/ordinary functions. Vague wording like 'repeats' or 'runs again' earns nothing on that point; part marks only if the core idea is clearly more than half there. Any wrong statement (e.g. a function that calls another function) loses the point it affects. Extra correct detail such as base case is fine but earns no extra marks._

- **P1** (3): States precisely that a recursive function is a function that calls itself (from within its own body), using the term 'function' and 'calls itself'. _Partial: Half (1.5) if it says the function repeatedly calls/uses itself or refers to itself only loosely, e.g. 'a function that repeats itself', without clearly stating it calls itself._
- **P2** (1): Makes clear the call to itself occurs inside the function's own definition/body (the function invokes itself during its execution, not merely being called by another function or in a loop).
- **P3** (1): Correctly distinguishes it from an iterative function/loop or ordinary function: a recursive function repeats via self-calls rather than loop constructs, or an ordinary function calls other functions, not itself.


## mohler/E11.Q06 (5 marks)

**Question:** What is the alternative way to solve a problem that could be solved through recursive functions?

**Model answer:** Through iteration.

_Marking stance: harsh. Full marks need the exact term "iteration" (P1), plus a precise mention of loops and a correct contrast with a function calling itself. Vague answers such as "another method" or "use a different function" earn nothing. Any wrong statement, such as naming another technique like pointers or overloading as the alternative, loses the affected point, and a wrong main answer loses P1._

- **P1** (3): States that the alternative to recursion is iteration, using the term 'iteration' (or iterative solution). _Partial: Half credit only if the answer names loops (for, while) as the alternative but does not use the term 'iteration'._
- **P2** (1): Correctly identifies the iterative approach as using loops (e.g. for, while, do-while) that repeat a block of code, rather than a function calling itself.
- **P3** (1): Correctly distinguishes iteration from recursion: iteration repeats via loops within one function, whereas recursion has a function call itself. No wrong statements about either.


## mohler/E11.Q07 (5 marks)

**Question:** What is the difference between an array that is declared as static and one that is not?

**Model answer:** The static arrays are intialized only once when the function is called.

_Marking stance: harsh. Full marks need the precise fact that a static array is initialized only once (on the first call) and the contrast that a non-static array is re-initialized on every call. Vague statements such as "static is permanent" or "static is fixed" without the initialization point earn nothing. Any wrong statement within a point, such as saying static arrays are re-initialized each call, voids that point._

- **P1** (3): States precisely that a static array is initialized only once (the first time the function is called / program-lifetime single initialization), not again on later calls. _Partial: Half credit (1.5) if it says the static array keeps or retains its values between calls but does not state it is initialized only once._
- **P2** (2): Correct contrast: a non-static (automatic/local) array is re-created and re-initialized every time the function is called. _Partial: Half credit (1) if it only says the non-static array is not preserved between calls, without stating re-initialization on each call._


## mohler/E11.Q08 (5 marks)

**Question:** What is the main difference between a string of characters that is read into a variable of type string versus a variable of type char []?

**Model answer:** The char [] will automatically add a null 0 character at the end of the string.

_Marking stance: harsh. Full marks need the precise fact: char [] automatically gets a null character ('\0') appended at the end, with an explicit contrast that type string does not. Vague answers such as "char [] is an array" or "string is easier to use" earn nothing. Any wrong statement about the null character, such as saying string adds it and char [] does not, loses the affected point._

- **P1** (3.5): States that a char [] (C-style character array / C-string) automatically has a null character ('\0', the null terminator) added at the end of the string when the input is read into it. _Partial: Half credit if the student says a terminating/end character is added to char [] but does not identify it precisely as the null character '\0'._
- **P2** (1.5): Correctly distinguishes from the string type: a variable of type string (the string class) does not require or show a null terminator added by the user/at the end of the data; it is not a null-terminated char array. The contrast must be explicit. _Partial: Half credit if the contrast is stated only vaguely, e.g. string handles its ending differently, without saying no null terminator is added._


## mohler/E11.Q09 (5 marks)

**Question:** Briefly describe the divide-and-conquer paradigm.

**Model answer:** Divide a problem into smaller subproblems, solve them recursively, and then combine the solutions into a solution for the original problem.

_Marking stance: harsh. Full marks need all three steps (divide into subproblems, solve recursively, combine into the original solution) stated precisely with the correct terms. Vague wording such as 'split it up and do each part' earns nothing for that step; only clearly more than half of a step earns half marks. Any wrong statement about a step (for example, saying the parts are solved independently of recursion, or that they are not combined) loses that point. Examples such as merge sort do not replace the description._

- **P1** (2): States that the problem is divided (split/broken down) into smaller subproblems (smaller instances of the same problem), using the term 'subproblems' or an exact equivalent such as 'smaller instances of the same problem'. _Partial: Half marks if only 'divide/break into smaller parts' is said without saying they are subproblems of the same problem._
- **P2** (1.5): States that the subproblems are solved recursively (the same method is applied to each subproblem, until a base case is reached or the subproblems are small enough to solve directly). _Partial: Half marks if 'solve the subproblems' is stated but recursion is not mentioned._
- **P3** (1.5): States that the solutions to the subproblems are combined (merged) into a solution for the original problem. _Partial: Half marks if 'combine the results' is stated without saying it produces the solution to the original problem._


## mohler/E11.Q10 (5 marks)

**Question:** Briefly describe in one sentence how does merge sort work?

**Model answer:** It splits the original array into two, sorts each of the two halves, and then merges the sorted arrays.

_Marking stance: harsh. Award full marks only when all three steps (split into two, sort each half, merge the sorted halves) are stated precisely in the correct order. Vague wording such as "it sorts the array by dividing" earns nothing for the point it fails to specify. A wrong description (e.g. choosing a pivot, swapping adjacent elements) costs the affected point; extra correct detail is fine._

- **P1** (1.5): States that merge sort splits/divides the original array into two (halves). _Partial: Says it divides/splits the array but does not say into two halves (or says into parts) — award 0.75 only if clearly stated._
- **P2** (1.5): States that each of the two halves is sorted (recursively sorted) separately. _Partial: Says the parts are sorted but not that each half is sorted individually — 0.75._
- **P3** (2): States that the two sorted halves/arrays are merged (combined) into one sorted array, using the term merge/merging. _Partial: Says the halves are combined/joined but without stating they are already sorted or without the term merge — 1._


## mohler/E12.Q01 (5 marks)

**Question:** What is a pointer?

**Model answer:** The address of a location in memory.

_Marking stance: harsh. Full marks need the precise fact: a pointer is an address of a location in memory, with the terms 'address' and 'memory location' used. Vague statements such as 'it points to something' or 'it refers to a variable' earn little or nothing; any wrong statement (e.g. a pointer is a value or a data type holding data) loses the affected point. Extra correct detail is allowed._

- **P1** (2.5): States that a pointer is an address (a memory address) — i.e. it holds/stores/is the address of something, using the term 'address'. _Partial: Half marks if it says it 'refers to' or 'points to' a variable or value but does not use the term address precisely._
- **P2** (1.5): States that the address is of a location in memory (a memory location, e.g. of a variable), using the terms 'location' and 'memory'. _Partial: Half marks if only 'memory' or only 'location' is mentioned without the full phrase._
- **P3** (1): Correctly distinguishes the pointer (an address/variable holding an address) from the value stored at that location, i.e. does not describe a pointer as the data/value itself.


## mohler/E12.Q02 (5 marks)

**Question:** What is the experimental approach for measuring the running time of an algorithm?

**Model answer:** Implement the algorithm and measure the physical running time.

_Marking stance: harsh. Full marks need both: the algorithm is implemented as a program AND its physical (actual clock) running time is measured. Vague answers such as 'test it' or 'see how fast it is' earn nothing or at most part marks as stated. Answers describing theoretical analysis, counting primitive operations or pseudocode/big-O earn no marks for the measurement point; any wrong statement about a point voids that point._

- **P1** (2): States that the algorithm must be implemented (written as an actual program/code in a programming language and run). _Partial: 1 mark if only 'run/test the algorithm' is stated without saying it is implemented as a program_
- **P2** (3): States that the physical (actual, real clock) running time is measured, e.g. using a timer/system clock, as opposed to counting operations or analysing theoretically. _Partial: 1.5 marks if 'measure the running time' is stated but without specifying physical/actual/clock time_


## mohler/E12.Q04 (5 marks)

**Question:** Briefly, how does selection sort work?

**Model answer:** It selects the minimum from an array and places it on the first position, then it selects the minimum from the rest of the array and places it on the second position, and so forth.

_Marking stance: harsh. Full marks need the precise idea: repeatedly pick the minimum of the remaining elements and put it in the next position, starting with the first. Part marks only when clearly more than half of a point is stated precisely. Vague statements ("it sorts by comparing elements"), wrong descriptions (e.g. swapping adjacent elements, or selecting the maximum to the front), or mixing with bubble/insertion sort earn nothing for that point._

- **P1** (2): States that selection sort selects/finds the minimum (smallest) element from the array and places/swaps it into the first position. _Partial: 1 mark if it says it finds the minimum but does not say it is placed in the first position (or vice versa) precisely._
- **P2** (2): States that the process then repeats on the remaining (unsorted) part of the array: select the minimum of the rest and place it in the second position, and so on for each following position. _Partial: 1 mark if repetition is stated but without clearly restricting it to the rest of the array or without mentioning the next position._
- **P3** (1): Makes clear the array is divided into a sorted part at the front that grows by one position each step, with the minimum always taken from the remaining unsorted part (not the whole array again), i.e. correctly distinguished from other sorts such as insertion or bubble sort that do not select a minimum.


## mohler/E12.Q05 (5 marks)

**Question:** What is the advantage of linked lists over arrays?

**Model answer:** Linked lists are dynamic structures, which allow for a variable number of elements to be stored.

_Marking stance: harsh. Full marks need the advantage stated precisely: linked lists are dynamic and hold a variable number of elements, contrasted with fixed-size arrays. Vague wording ("more flexible", "easier") earns nothing on a point. Any wrong claim (e.g. faster random access, less memory per element) loses the point it affects; answers about other advantages and not size earn 0._

- **P1** (2.5): States that linked lists are dynamic data structures (size can grow/shrink at run time, not fixed in size like arrays), using the term 'dynamic'. _Partial: Half if it says size is not fixed / can change but does not use the term dynamic or does not contrast with fixed-size arrays._
- **P2** (1.5): States that this allows a variable number of elements to be stored (elements can be added or removed freely without declaring or fixing the capacity in advance).
- **P3** (1): Correctly distinguishes from arrays: arrays have a fixed size/capacity set at declaration (static), so a linked list's advantage is its flexible size.


## mohler/E12.Q06 (5 marks)

**Question:** What is a queue?

**Model answer:** A data structure that stores elements following the first in first out principle. The main operations in a queue are enqueue and dequeue.

_Marking stance: harsh. Full marks need a queue defined as a data structure, the FIFO principle stated precisely, and both enqueue and dequeue named. Part marks only as stated in partial_credit. Describing a stack (LIFO), swapping the operations' meanings, or giving only a real-world analogy without the technical terms earns nothing for the affected point._

- **P1** (1): States that a queue is a data structure that stores elements (a linear collection of elements).
- **P2** (2): States precisely that elements are processed in First In First Out (FIFO) order: the first element inserted is the first removed. Must use FIFO / first in first out; a vague 'ordered' or 'line' statement is not enough. _Partial: 1 mark if the idea of the earliest-added element being removed first is described but the term FIFO / first in first out is not used precisely_
- **P3** (2): Names both main operations: enqueue (insert at the rear/back) and dequeue (remove from the front). _Partial: 1 mark if only one of enqueue or dequeue is named correctly_


## mohler/E12.Q07 (5 marks)

**Question:** What are the main operations associated with a stack?

**Model answer:** push and pop

_Marking stance: harsh. Full marks need both push and pop named with the correct terms, and no wrong operations given as main ones. Each missing operation loses its point. A wrong extra item (e.g. enqueue, dequeue, insert at the bottom) or a swapped description costs the point it affects. Vague wording such as "add and remove" without the terms push and pop earns nothing for that point._

- **P1** (2.5): States "push" as a main stack operation, correctly described if described at all: adds/inserts an element onto the top of the stack. _Partial: Names push but gives a wrong or incomplete description; otherwise nothing if push is absent._
- **P2** (2.5): States "pop" as a main stack operation, correctly described if described at all: removes the top element of the stack (LIFO order). _Partial: Names pop but gives a wrong or incomplete description; otherwise nothing if pop is absent._


## mohler/E12.Q08 (5 marks)

**Question:** What is the Euler tour traversal of a tree?

**Model answer:** A walk around the tree, starting with the root, where each node is seen three times: from the left, from below, from the right.

_Marking stance: harsh. Full marks need all three elements stated precisely: a walk around the tree starting at the root, each node seen three times, and the three visits being left, below, right. Part marks only where clearly more than half of a point is stated, as set out in each point. Vague answers (e.g. just "visits all nodes", or naming only preorder/inorder/postorder without the three-visits-per-node idea) earn nothing for the affected point, and a wrong count or wrong visit names loses that point._

- **P1** (1.5): States that the Euler tour traversal is a walk around the tree that starts at the root (traverses the whole tree by walking around it). _Partial: Half if it says it is a walk/traversal around the tree but does not say it starts at the root (or vice versa)._
- **P2** (1.5): States that each node is visited/seen three times during the walk. _Partial: Half if it says nodes are visited multiple times without stating three._
- **P3** (2): Names the three visits precisely: from the left (before the left subtree / preorder-like), from below (between subtrees / inorder-like), and from the right (after the right subtree / postorder-like). _Partial: Half if two of the three visits are correctly named; none if any is wrong._


## mohler/E12.Q09 (5 marks)

**Question:** How do you delete a node from a binary search tree?

**Model answer:** Find the node, then replace it with the leftmost node from its right subtree -LRB- or the rightmost node from its left subtree -RRB- .

_Marking stance: harsh. Full marks need all three: find the node, replace with the leftmost node of the right subtree, and the alternative rightmost node of the left subtree, all with correct terms. Wrong pairing (e.g. leftmost of the left subtree) or only vague wording like "replace with a child" or "rearrange the tree" earns nothing for that point. Merely describing leaf/one-child cases without the replacement rule earns no marks for P2 or P3._

- **P1** (1): States that the node to be deleted must first be found/located in the tree (search for the node by key).
- **P2** (2.5): States that the node is replaced by the leftmost node (the minimum / in-order successor) of its right subtree, stated precisely as leftmost node of the RIGHT subtree. _Partial: Names the right subtree successor or the left subtree predecessor correctly but without saying leftmost/rightmost (or minimum/maximum) precisely: 1.25_
- **P3** (1.5): States the alternative: replace it with the rightmost node (the maximum / in-order predecessor) of its LEFT subtree, with the correct pairing of leftmost-with-right and rightmost-with-left. _Partial: Alternative mentioned with the correct subtree but the extreme node (rightmost/maximum) not named: 0.75_


## mohler/E12.Q10 (5 marks)

**Question:** How many steps does it take to search a node in a binary search tree?

**Model answer:** The height of the tree.

_Marking stance: harsh. Full marks need the precise term 'height of the tree' as the number of steps, plus the worst-case/longest-path idea and the distinction from the node count n. Vague answers such as 'it depends on the tree' or 'a few comparisons' earn nothing. Any wrong statement, such as saying the steps always equal n or always log n, loses the point it affects._

- **P1** (3): States that the number of steps to search a node in a BST is given by the height of the tree (i.e., proportional to/at most the height h, O(h)), using the term 'height'. _Partial: Half credit if the answer relates it to tree depth/levels or path length from root without using the term height precisely._
- **P2** (1): Makes clear that this is the worst-case count, being the longest root-to-leaf path (the number of levels traversed), not the total number of nodes n.
- **P3** (1): Correctly distinguishes that the steps depend on height rather than the number of nodes: e.g., a balanced tree gives about log n steps while a skewed tree gives up to n steps.
