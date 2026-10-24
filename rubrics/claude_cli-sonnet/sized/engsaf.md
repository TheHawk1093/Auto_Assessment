# engsaf: sized rubrics

Marks per point add up to the question total.

## engsaf/010be1a486 (2 marks)

**Question:** Define Priority Inversion in single line.

**Model answer:** a higher priority process not getting CPU due to a lower priority process, because the lower priority process holds a resource

- **P1** (1): States that a higher-priority process/task is prevented from running (does not get the CPU) or is made to wait/blocked.
- **P2** (1): States that this is caused by a lower-priority process holding a resource (e.g., lock/semaphore) that the higher-priority process needs. Equivalent wording accepted.


## engsaf/051fb4eb5a (2 marks)

**Question:** Define noise in a time-series data

**Model answer:** Noise means random fluctuations in time series data about its typical pattern. Two types of noise: White noise and red noise.

- **P1** (1): Defines noise as random fluctuations/irregular variations in time series data about its typical (underlying/expected) pattern. Equivalent wording accepted.
- **P2** (1): States that there are two types of noise: white noise and red noise. _Partial: Half credit if only one of white noise or red noise is named._


## engsaf/0d56094c86 (2 marks)

**Question:** Consider 5 replicas N1, N2, N3, N4, and N5 running the RAFT protocol to main- tain a consistently replicated log for some application. The nodes have received the fol- lowing entries: a, b, c in term 1, p, q, r s in term 2, and x, y, z in term 3. The content of the logs of nodes N1 to N4 are as follows. N1: (a, b, p, q, x, y), N2: (a, b, p, q, x, y, z),N3: (a, b, p, q, r, s), N4: (a, b, c). The log at N5 is not provided to you. Which of the nodes was likely not a leader in any of the three terms? Justify your answer.

**Model answer:** In term 1 , N4 could have been the leader. In term 2, N3 could have been the leader. In term 3, N2 could have been the leader. N1 was never a leader

- **P1** (1): States that N1 was likely never a leader in any of the three terms (N5 is not the answer).
- **P2** (1): Justifies by showing the other nodes can account for the leaders of the terms: N4 (a, b, c) could be the term 1 leader, N3 (…, r, s) the term 2 leader, and N2 (…, x, y, z) the term 3 leader. Equivalent reasoning, e.g. each of these logs holds the full set of entries of that term, earns the mark. _Partial: Half if only two of the three term leaders are correctly identified/justified._


## engsaf/0fa4f95afa (2 marks)

**Question:** What are the two important scales in Hydrology? ---------------------

**Model answer:** Availability of driking water, time scale, length of the process, spatial scale.

- **P1** (1): Identifies time scale (e.g. length/duration of the process) as one of the two important scales in hydrology. Equivalent wording accepted.
- **P2** (1): Identifies spatial scale (e.g. length/size of the area over which the process occurs) as the other important scale. Equivalent wording accepted.


## engsaf/1c89ab7d7a (2 marks)

**Question:** Define meteorological drought.

**Model answer:** meteorological draught is caused by the condition leading from the excessive reduction in the level of ground water. This condition usually occurs at low rainfall area with excessive usage of ground water.

- **P1** (1): States that meteorological drought is a condition arising from a reduction/deficit (e.g. of water/ground water level, as in the model answer) leading to dryness. Equivalent wording accepted.
- **P2** (1): States that it usually occurs in areas of low rainfall combined with excessive usage of (ground) water. Equivalent wording accepted. _Partial: Half credit if only low rainfall or only excessive water usage is mentioned._


## engsaf/279135dd2f (2 marks)

**Question:** Write any two limitations of AJM.

**Model answer:** Low Material removal rate (MRR) , Limited nozzle life, High cost

- **P1** (1): First valid limitation of AJM (abrasive jet machining), e.g. low material removal rate, limited nozzle life/nozzle wear, high cost, or an equivalent correct limitation (e.g. abrasive embedding, poor accuracy/taper, cannot machine soft materials).
- **P2** (1): Second, different valid limitation of AJM from the same kind of list. Equivalent wording accepted; must be distinct from the first.


## engsaf/28b66fb9e2 (2 marks)

**Question:** c. Assume the OS is using a lazy allocation policy for memory allocation to processes. On a page fault due to an unmapped physical page(and a valid virtual address), the OS handles the page fault (via allocation and updates to the virtual to physical address mappings in the page table) and then executes the next instruction (the one after the faulting instruction).

**Model answer:** FALSE Fixing the mapping is only part of operations, the OSes page fault handler creates the mappings and returns from the handler and re-executes the faulting instruction. On a page fault the PC is not incremented.

- **P1** (1): States the statement is FALSE.
- **P2** (1): Explains that after the handler creates the mapping, the faulting instruction is re-executed (PC is not advanced to the next instruction). Equivalent wording accepted.


## engsaf/36dc74b1c6 (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. No correct justification, no marks. e. If a parent process forks a new child process, the exec system call can be used in the parent process before the child process terminates.

**Model answer:** True, parent and child are entirely two different processes. Parent can perform any operation that it wants including exec.

- **P1** (0.5): States TRUE.
- **P2** (1.5): Justifies that parent and child are separate processes (own address space/independent execution), so the parent is free to perform any operation, including calling exec, regardless of whether the child has terminated. Equivalent wording accepted. A justification is required; without it no marks are given (including for P1).


## engsaf/43bce9f945 (2 marks)

**Question:** What is an orthotropic material ?

**Model answer:** Orthotropic materials have 9 elastic constants.They also have material properties at a particular point which differ along 3 orthogonal axes.

- **P1** (1): States that an orthotropic material has 9 independent elastic constants (equivalent wording accepted).
- **P2** (1): States that at a point its material properties differ along three mutually orthogonal axes (three orthogonal planes/directions of symmetry; equivalent wording accepted).


## engsaf/469f7bbe77 (2 marks)

**Question:** Give two uses of lasers

**Model answer:** cutting and welding purpose, used in medical surgery, optical fibre communication , laser printing are some uses of lasers.

- **P1** (1): States one valid use of lasers (e.g. cutting/welding, medical surgery, optical fibre communication, laser printing, or other correct use). Equivalent wording accepted.
- **P2** (1): States a second, different valid use of lasers (e.g. cutting/welding, medical surgery, optical fibre communication, laser printing, or other correct use). Must be distinct from the first.


## engsaf/4e1c02f246 (2 marks)

**Question:** What are all the common materials that serve as nuclei for ice crystal formation?

**Model answer:** dust particles - clay minerals, organic and ordinary ocean salts

- **P1** (1): Names dust particles (including clay minerals) as ice nuclei.
- **P2** (1): Names organic particles and ordinary ocean (sea) salts as ice nuclei. Equivalent wording accepted. _Partial: Half credit (0.5) if only one of organic material or ocean salts is given._


## engsaf/544ff94842 (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. [6 marks] No correct justification, no marks. f. A spinlock is called a spinlock, as each attempt to acquire the lock will need spinning on the CPU (checking for lock status more than once), before the lock can be acquired.

**Model answer:** FALSE If the lock is available a spinlock does not have to spin.

- **P1** (1): States FALSE.
- **P2** (1): Justifies that if the lock is available (free) when the attempt is made, the spinlock is acquired immediately without spinning; spinning happens only when the lock is held. Equivalent wording accepted. No marks if justification is missing or wrong.


## engsaf/5631b84b94 (2 marks)

**Question:** To segment the rose petals [4 marks]:

**Model answer:** To segment rose petals H (Hue) -- Narrow range around 0/360 degress ( Red has hue of 0) S (saturation) -- Close to 0.8-1 (Red is primary color and all primary colors are pure colors) I (intensity) -- Broad range around 0.5

- **P1** (1): Hue: states a narrow range of hue around 0°/360° (red).
- **P2** (1): Saturation: states high saturation, close to 0.8–1 (pure colour). Intensity: states a broad range around 0.5 (mid-level, not restrictive). _Partial: Half (0.5) for saturation correct only or intensity correct only._


## engsaf/5a89251dec (2 marks)

**Question:** What are the key assumptions of the Muskingum flood routing method?

**Model answer:** In Muskingum method k and x are assumed to be constant and doesn't change with respect to time but changes with respect to shape of the channel in reach.The relation between the outflow discharge and the inflow discharge is linear in nature with a value of m = 1. weighing factor x = 1 valid for only channel routing.

- **P1** (1): States that the parameters K and x are constant (do not change with time) for the channel reach, depending only on the reach/channel characteristics (shape).
- **P2** (1): States that the storage–discharge relationship is linear (storage related linearly to weighted inflow and outflow, exponent m = 1), and that the method applies to channel routing. _Partial: Half credit if only linearity/m = 1 or only channel-routing applicability is given._


## engsaf/6c639305d5 (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. [6 marks] No correct justification, no marks. a. Since the OS knows that it executes on a CPU and interacts with IO devices via the CPU, the instruction set architecture is not an abstraction provided by the CPU to the OS.

**Model answer:** FALSE The ISA is an abstraction instructions are mapped to functionality, how the functionality is achieved is not known to the OS, but the ISA instructions + registers are used by the OS for its functionality. Key point - Implementation details/achievement of functionality is not known to the OS. OS understands the ISA, in fact an OS needs to be compiled differently for different ISAs.

- **P1** (0.5): States FALSE.
- **P2** (1.5): Justification: the ISA is an abstraction provided by the CPU. Instructions (and registers) map to functionality, and the OS uses them, but how that functionality is implemented in hardware is hidden from the OS. Equivalent wording accepted, e.g. the OS knows the ISA but not implementation details, or the OS must be compiled differently for different ISAs. _Partial: Half credit if the answer says only that the ISA is an abstraction or that the OS uses ISA instructions, without saying implementation details are hidden from the OS._


## engsaf/755c9c7e80 (2 marks)

**Question:** What is vapor pressure deficit?

**Model answer:** the difference between the amount of moisture in the air and how much moisture saturated air can hold

- **P1** (1): States that vapor pressure deficit is a difference (between two moisture quantities): the amount of moisture currently in the air versus the maximum it could hold.
- **P2** (1): Identifies the two quantities correctly: the actual moisture content of the air, and the moisture that saturated air can hold (saturation level) at the same conditions. Equivalent wording accepted.


## engsaf/7866562480 (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. No correct justification, no marks. a. The pipe system call creates two file descriptors fd[0] and fd[1]. Writes using fd[1] can be read using fd[0] but not vice-versa.

**Model answer:** True, pipe system call only allows for one directional read. Read can only be done from fd[0] and write can only be done at fd[1].

- **P1** (0.5): States TRUE.
- **P2** (1.5): Justification: pipe is unidirectional — data written to fd[1] (write end) is read from fd[0] (read end); fd[0] is used only for reading and fd[1] only for writing, so it cannot be done the other way round. Equivalent wording accepted. No marks if justification is missing or incorrect.


## engsaf/7870a031ef (2 marks)

**Question:** Expand the term SWOT

**Model answer:** SWOT stands for Strengh Weakness Opportunity Threats

- **P1** (1): Correctly gives Strengths and Weaknesses as the first two terms (S = Strength, W = Weakness). Minor spelling errors are accepted. _Partial: Half (0.5) if only one of Strength or Weakness is correct._
- **P2** (1): Correctly gives Opportunities and Threats as the last two terms (O = Opportunity, T = Threat). Minor spelling errors are accepted. _Partial: Half (0.5) if only one of Opportunity or Threat is correct._


## engsaf/88153ceac6 (2 marks)

**Question:** In what situation a canal fall is provided?

**Model answer:** When the natural slope of the region is more than the canal slope being provided.

- **P1** (2): States that a canal fall is provided when the natural (ground) slope of the region/country is steeper (greater) than the canal's designed bed slope. _Partial: 1 mark if only says the ground slope is steep or the terrain is sloping, without comparing it to the canal slope (or the comparison is stated unclearly)._


## engsaf/916419680e (2 marks)

**Question:** Under which circumstances is a multilayer perceptron neural network with multiple hidden layers (&gt;1 layer) desirable?

**Model answer:** when more deep learning or critical learning of features are required, then more hidden layers are required to extract out and learn feautres properly and efficiently so as to perform further tasks well. example- multiclass classification, XOR function

- **P1** (1): States that multiple hidden layers are desirable when the task requires learning deeper/more complex or critical features (hierarchical feature extraction), i.e. when a single hidden layer is insufficient to extract and learn the features properly and efficiently. Equivalent wording accepted.
- **P2** (1): Gives a suitable example of such a task, e.g. multiclass classification or XOR-type (non-linearly separable) problems, or another valid complex task.


## engsaf/956d741e7b (2 marks)

**Question:** a. List and explain two privileged actions that an user process may attempt to perform and which are prevented by the OS via the limited-directed execution setup. Note that the user process has to know specifically how to make such an attempt. (e.g., the user process does not know that a PCB exists and hence may not know how to update its contents).

**Model answer:** - Write to CR3 register to modify page directory pointer - Write to the EFLAGS registers to modify execution status (zero bit, interrupt enable/disable) - Write to the IDTR register to change location of IDT - Access to VA that lies in the kernel virtual address range

- **P1** (1): First valid privileged action named and explained: e.g. writing to CR3 (change page directory pointer), writing EFLAGS (change execution status/interrupt enable), writing IDTR (change IDT location), or accessing a kernel-range virtual address. Must state what the action does/would change; the OS/hardware prevents it (e.g. via privilege level/trap). _Partial: Half if the action is named correctly but the explanation of what it does is missing or vague._
- **P2** (1): Second, different valid privileged action named and explained, from the same kind of list (CR3 write, EFLAGS write, IDTR write, kernel VA access, or an equivalent privileged action a user process could specifically attempt). Equivalent wording accepted. _Partial: Half if the action is named correctly but the explanation is missing or vague._


## engsaf/9668c8b064 (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. [6 marks] No correct justification, no marks. d. An executable (binary) program can be used to instantiate and execute more than one process simuitaneous.y. In such a situation, processes of the same program use the same PCB process-conro.Dock, with a reference counter to indicate number of instances,

**Model answer:** FALSE Each process is an independent entity and needs a separate OS state to track its execution memory contents, open files, memory allocations, stack state etc. A shared PCB cannot provide this semantics.

- **P1** (1): States FALSE (the statement is incorrect).
- **P2** (1): Justifies: each process is an independent entity needing its own separate PCB/OS state (e.g., execution state, memory contents/allocations, open files, stack), so a single shared PCB with a reference counter cannot provide this. Equivalent wording accepted.


## engsaf/99c0cd759e (2 marks)

**Question:** Write any advantage of using TiC/TiN as a tool coating material.

**Model answer:** excellent wear resistance thermal stability low coefficient of friction improves thermal transfer increases tool life.

- **P1** (1): States one valid advantage of TiC/TiN coating, e.g. excellent wear resistance, thermal stability, low coefficient of friction, improved thermal transfer, or increased tool life (equivalent wording accepted).
- **P2** (1): Gives a brief correct supporting statement or consequence for that advantage (e.g. reduced friction/wear leads to longer tool life, or high hardness resists abrasion), or a second valid advantage from the list.


## engsaf/9b31c7b110 (2 marks)

**Question:** What are the critical issues involved in design of an online compression system for space applications?

**Model answer:** Data rate should not exceed the channel capacity. Full capacity of the communication channel should be utilized. Maximum quality should be preserved.

- **P1** (0.75): States that the output data rate must not exceed the capacity of the communication channel.
- **P2** (0.75): States that the full capacity of the communication channel should be utilized (no wasted bandwidth).
- **P3** (0.5): States that maximum quality (of the reconstructed data) should be preserved.


## engsaf/a23fae8ca6 (2 marks)

**Question:** Two advantages of separating declaration from definition are: .....

**Model answer:** The code will be more clear and easier for the reader to understand. Allows easy changing, debugging, and overriding of the functions. Enhances modularity of the code. This also separates the abstraction from the implementation.

- **P1** (1): States one valid advantage of separating declaration from definition (e.g., clearer/easier to understand code, easier changing/debugging/overriding of functions, enhanced modularity, or separating abstraction/interface from implementation).
- **P2** (1): States a second, different valid advantage from the same set (equivalent wording accepted). It must be distinct from the first, not a rewording of it.


## engsaf/aecb888a50 (2 marks)

**Question:** What do you mean by empirical equations?

**Model answer:** equations derived from experiments/observed data. they don't have a mathematical proof behind them

- **P1** (1): States that empirical equations are derived from experiments, observations or measured data (rather than from theory).
- **P2** (1): States that they have no rigorous mathematical/theoretical proof or derivation behind them (equivalent wording accepted, e.g. based on curve fitting/experience, not theoretically derived).


## engsaf/bb6ba9c65e (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. No correct justification, no marks. a. The pipe system call creates two file descriptors fd[0] and fd[1]. Writes using fd[0] can be read using fd[0] or vice-versa (read on fd[1] and write on fd[0]).

**Model answer:** False, write can only be done on fd[1] and read can only be done from fd[0].

- **P1** (0.5): States FALSE (the statement is not correct).
- **P2** (1.5): Justification: in a pipe, fd[1] is the write end and fd[0] is the read end; data can only be written via fd[1] and read via fd[0], so writing on fd[0] / reading on fd[1] is not possible. Equivalent wording accepted. No marks if justification is missing or wrong.


## engsaf/ce2c7412c7 (2 marks)

**Question:** Region of rejection in hypothesis testing is

**Model answer:** range of values that lead to rejection of null hypothesis

- **P1** (1): States that the region of rejection (critical region) is a range/set of values (of the test statistic or sample outcomes, e.g. the tail area(s) of the distribution).
- **P2** (1): States that if the test statistic falls in this range, the null hypothesis is rejected. Equivalent wording accepted.


## engsaf/ce468a17bf (2 marks)

**Question:** The desirable properties of an estimator in statistics are

**Model answer:** Unbiased, Consistency, Efficiency and Sufficiency

- **P1** (1): Lists unbiasedness and consistency as desirable properties of an estimator. _Partial: Half (0.5) if only one of the two is given._
- **P2** (1): Lists efficiency and sufficiency as desirable properties of an estimator. _Partial: Half (0.5) if only one of the two is given._


## engsaf/cff26045f8 (2 marks)

**Question:** Two advantages of using multiple based valuation method are _________________________ and _________________________________

**Model answer:** Quick and Convenient, Market Based data reflecting the markets growth and risk expectations.

- **P1** (1): First advantage: multiple-based valuation is quick / convenient / simple to use (equivalent wording such as easy, fast to calculate).
- **P2** (1): Second advantage: it uses market-based data, reflecting the market's growth and risk expectations (equivalent such as reflects current market sentiment/pricing of comparable firms).


## engsaf/d119a19a7a (2 marks)

**Question:** Write any ONE limitation of the wireframe modeling system.

**Model answer:** The representation is ambiguous and one wireframe model can represent different solid objects in the wireframe model. it can become messy and confusing.

- **P1** (1): States a valid limitation of wireframe modeling, e.g. the representation is ambiguous / one wireframe can be interpreted as several different solid objects (or equivalently: it becomes messy/confusing, lacks surface and volume information, hidden lines cannot be removed). Equivalent wording accepted; any one valid limitation earns the mark.
- **P2** (1): Gives a brief explanation or consequence of the stated limitation (e.g. one wireframe model can represent different solids so the shape is unclear, or complex models become cluttered and confusing to read).


## engsaf/d321cc3922 (2 marks)

**Question:** Three key principles of ISO series are ., ...and .

**Model answer:** Consensus , Industrial wide applicability and Voluntary Nature

- **P1** (0.5): Names Consensus as one principle.
- **P2** (0.5): Names Industry-wide applicability as one principle (equivalent wording accepted).
- **P3** (0.5): Names Voluntary nature as one principle (equivalent wording accepted).
- **P4** (0.5): All three principles are given correctly, with no incorrect extra principles replacing them.


## engsaf/dee7f5df0c (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. No correct justification, no marks. d. Assuming an user process knows the PID of another task from a pool of several READY processes, it does not have the capability to initiate a context switch and schedule the target process next on the CPU.

**Model answer:** True, the user process has no control over which process will be scheduled next by the scheduler

- **P1** (1): States TRUE (the statement is correct).
- **P2** (1): Justifies that the user process has no control over which process the scheduler picks next / cannot force a context switch to a chosen process, since scheduling is done by the kernel scheduler (equivalent wording accepted).


## engsaf/e8d593831e (2 marks)

**Question:** To segment the green leaves and stem [4 marks]:

**Model answer:** Hue should be centered around 120 degrees for green color. Intensity should be ranged around 0.5. Saturation range should also be around 0.5 as some blackish portion is seen in the stem. In this case, The saturation is low .

- **P1** (1): States that hue should be centered around 120 degrees (green). Equivalent wording accepted.
- **P2** (1): States that intensity and saturation ranges should be moderate (around 0.5), noting the blackish portion of the stem gives low saturation. Equivalent wording accepted. _Partial: Half if only one of intensity or saturation is given a range around 0.5._


## engsaf/ebd39016dd (2 marks)

**Question:** Describe the purpose of state DecideAction in adacrus node (max 2-3 lines).

**Model answer:** DecideAction node was used to decide which direction the bot should turn next like left/ right or take a U-turn depending on the state of the robot.

- **P1** (1): States that the DecideAction state/node decides the robot's next action/direction of movement (which way the bot should go next).
- **P2** (1): Mentions the possible choices (turn left, turn right, or take a U-turn) and/or that the decision depends on the current state/situation of the robot. Equivalent wording accepted.


## engsaf/ecc261cec7 (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. No correct justification, no marks. e. If a parent process forks a new child process, the exec system call cannot be used in the parent process until the child process terminates.

**Model answer:** False, parent and child processes are two independent processes. Parent can perform any operation that it likes including an exec system call.

- **P1** (0.5): States FALSE.
- **P2** (1.5): Justification: parent and child are two independent processes, so the parent can perform any operation, including calling exec, without waiting for the child to terminate (equivalent wording accepted). No marks for P2 if the answer is not FALSE.


## engsaf/ed8c1ccac6 (2 marks)

**Question:** Q1. State TRUE or FALSE and justify. No correct justification, no marks. d. Without the timer interrupt, the OS still has opportunities to schedule READY processes and share the CPU for multitasking

**Model answer:** True, the OS can use system calls as an event when it schedules some other process on the CPU to run. Various other events can also be seen as opportunities by the OS to perform scheduling operations

- **P1** (0.5): States TRUE.
- **P2** (1.5): Justifies that the OS can still schedule at other events, e.g. system calls (process blocks/yields/exits via a system call, so the OS can run another process), or other events such as I/O interrupts or other traps. Equivalent wording accepted; at least one valid non-timer scheduling opportunity must be given.


## engsaf/ee9ee990d5 (2 marks)

**Question:** How is regularized set operation helpful in solid modeling?

**Model answer:** boundaries are defined. no dangling edges. no edges are created extra and no edges are lost while taking intersection of two objects.Regularized set operation helps to follow the defined process in predefined sequence

- **P1** (1): States that regularized set operations keep the solid's boundaries properly defined / valid, so the result has no dangling edges or faces (the result is always a valid closed solid).
- **P2** (1): States that no extra edges are created and no edges are lost when combining objects (e.g. intersection), or that the operation follows the defined process in a predefined sequence; equivalent wording accepted.


## engsaf/f1be87d27a (2 marks)

**Question:** State any two reasons for electrical charge on the surface of colloidal particles.

**Model answer:** Ionisation of active sites such as OH and COOH groups depending on pH of medium. Imperfection in crystal structure ( atoms of low valency replace silicon reducing positive charge, hence net charge becomes negative), Adsorption of anions onto the surface of particles.

- **P1** (1): First valid reason for charge on colloidal particles (any one of: ionisation of surface active sites such as OH/COOH groups depending on pH; imperfection in crystal structure, e.g. lower-valency atoms replacing silicon giving net negative charge; adsorption of ions/anions onto the particle surface). Equivalent wording accepted.
- **P2** (1): Second, different valid reason from the same list. Must be distinct from the first reason.


## engsaf/f86e9565df (2 marks)

**Question:** Suppose a high-resolution image of an urban area is being captured from space. If the roads are to be put in different categories, what features may be useful?

**Model answer:** Possible features which could very wilh different types of roads are: Edge detection, Road width, length of the road, Color of the road . Road length between two junctions / dead ends. Road edges or shadows to classify bridges and flyovers.

- **P1** (1): Names at least two relevant appearance/shape features useful for classifying roads, such as road width, colour/texture of the road surface, or edges (edge detection). Equivalent valid features earn credit. _Partial: Half (0.5) if only one such feature is named._
- **P2** (1): Names at least one structural/contextual feature, such as road length between junctions/dead ends, or road edges/shadows used to identify bridges and flyovers. Equivalent valid features earn credit.


## engsaf/fcc52559d7 (2 marks)

**Question:** List down the types of irrigation methods? ________________

**Model answer:** Sprinkler Irrigation, Drip irrigation, Furrow Method, Flood Method

- **P1** (1): Lists at least two correct irrigation methods from: sprinkler, drip, furrow, flood (equivalent names such as surface/basin/border accepted if correct). _Partial: Half (0.5) if only one correct method is listed._
- **P2** (1): Lists all four methods: sprinkler irrigation, drip irrigation, furrow method, and flood method (equivalent wording accepted). _Partial: Half (0.5) if three of the four are listed._


## engsaf/febbc2c2ac (2 marks)

**Question:** Write three parameters which affect MRR in ultrasonic machining ?

**Model answer:** Frequency of vibration, Amplitude of vibration, Abrasive slurry concentration, Slurry Particle Diameter

- **P1** (0.67): First valid parameter affecting MRR in ultrasonic machining (e.g. frequency of vibration, amplitude of vibration, abrasive slurry concentration, abrasive particle diameter). Equivalent wording accepted.
- **P2** (0.67): Second distinct valid parameter from the same set (or an equivalent correct parameter).
- **P3** (0.66): Third distinct valid parameter from the same set (or an equivalent correct parameter).
