# saf: harsh rubrics

Marks per point add up to the question total.

## saf/DLL_2.1 (1 marks)

**Question:** Name the 3 service classes the Data Link Layer offers and explain the differences between the classes.

**Model answer:** 1.unconfirmed connectionless - no ACK, loss of data possible, no flow control, no connect or disconnect. 2.confirmed connectionless - with ACK, no loss of data (timeout and retransmit instead→ duplicates and sequence errors possible), no flow control, no connect or disconnect. 3.connection-oriented - no data loss, duplication or sequencing errors. Instead a 3 phased communication with connect and disconnect, and flow control

_Marking stance: harsh. Harsh: each class's differences must be stated precisely with the correct terms (ACK, flow control, connect/disconnect, duplicates/sequencing errors). Vague statements such as 'one is more reliable' earn nothing. A wrong detail (e.g. saying confirmed connectionless has flow control or connection setup) cancels that point._

- **P1** (0.25): Names all three classes correctly: unconfirmed connectionless, confirmed connectionless, connection-oriented (all three required, with correct terms). _Partial: Two of the three named correctly gives half._
- **P2** (0.25): Unconfirmed connectionless: no acknowledgement, data loss possible, no flow control, no connect/disconnect (must state no ACK and loss possible, plus at least no connection setup). _Partial: No ACK and loss of data stated, but no mention of flow control/connection setup, gives half._
- **P3** (0.25): Confirmed connectionless: uses ACK, no loss of data but timeout and retransmission can cause duplicates and sequencing errors, no flow control, no connect/disconnect. _Partial: ACK and no loss stated but duplicates/sequence errors omitted (or the reverse) gives half._
- **P4** (0.25): Connection-oriented: no data loss, no duplication, no sequencing errors; three-phase communication (connect, data transfer, disconnect) with flow control. _Partial: Reliability (no loss/duplicates/sequence errors) stated, but three phases or flow control missing, gives half._


## saf/DLL_2.2 (1 marks)

**Question:** What is the difference between asynchronous and synchronous transmission mode in the Data Link Layer.

**Model answer:** Asynchronous transmission: Every character a self-contained unit surrounded by a start bit and a stop bit, which is an easy and cheap pattern, but causes low transmission rates. Synchronous transmission: Several characters pooled to a continuous stream of data (frames), Frames defined by SYN or flag, higher complexity, but higher transmission rates. Requires synchronization between sender and receiver.

_Marking stance: harsh. Full marks need both modes described with the specific features: start/stop bit per character versus frames of pooled characters delimited by SYN/flag, plus the trade-offs (cost/rate/complexity/synchronization). Generic statements like "async is slower" without the stated detail earn nothing for that point. Any wrong detail (e.g. start/stop bits attributed to synchronous mode) cancels that point._

- **P1** (0.25): Asynchronous transmission: each character is sent as a self-contained unit framed by a start bit and a stop bit. _Partial: Only one of start bit / stop bit mentioned, or self-contained character unit without start/stop bits._
- **P2** (0.25): Asynchronous transmission is simple/cheap but gives low transmission rates. _Partial: Only one of simple/cheap or low rate stated._
- **P3** (0.25): Synchronous transmission: several characters are pooled into a continuous stream of data (frames), with frames delimited by SYN characters or flags. _Partial: Continuous stream/frames of many characters stated but delimiting by SYN/flag missing (or the reverse)._
- **P4** (0.25): Synchronous transmission has higher complexity but higher transmission rates, and requires synchronization between sender and receiver. _Partial: Two of the three (higher complexity, higher rate, sender-receiver synchronization) stated._


## saf/DLL_2.3 (1 marks)

**Question:** What requirement has to be met so that you can use the piggybacking extension to the sliding window protocol?

**Model answer:** Piggybacking only makes sense if there is a full-duplex or semi-duplex connection between sender and receiver i.e. two-way communication or Frames must contain additional field for acknowledgement.

_Marking stance: harsh. Full marks need both: the duplex (two-way) connection, named precisely, and the extra acknowledgement field in data frames. Part marks only for a clear but imprecise version of one element, e.g. 'two-way communication' without the duplex term. A wrong statement, such as requiring simplex, or a vague answer like 'needs sliding window' earns nothing for that point._

- **P1** (0.5): States that the connection must be full-duplex (or semi-duplex/half-duplex), i.e. two-way communication in which both sender and receiver send data frames. _Partial: Only says 'two-way communication' or 'data flows both directions' without naming duplex: 0.25_
- **P2** (0.5): States that data frames must contain an additional field for the acknowledgement (ACK number), so that the acknowledgement can be carried in an outgoing data frame instead of a separate ACK frame. _Partial: Says acknowledgements are attached to/sent with data frames but does not state a frame field is needed: 0.25_


## saf/IPP_6.1 (1 marks)

**Question:** What are the objectives of IPv6? Please state at least 4 objectives.

**Model answer:** To support billions of end-systems. To reduce routing tables. To simplify protocol processing with Simplified header. To increase security. To support real time data traffic (quality of service). Flow label, traffic class. To provide multicasting. To support mobility (roaming). To be open for change (future): extension headers for additional change incorporation. To coexistence with existing protocols.

_Marking stance: harsh. Full marks need at least four distinct, correct IPv6 objectives from the model answer list, each worth 0.25. Each objective must be stated precisely with the right term (e.g. simplified header, flow label/QoS, extension headers); vague or generic statements such as 'faster' or 'better' earn nothing. A wrong or non-IPv6 objective earns nothing for that point, and repeated objectives count once._

- **P1** (0.25): First correct objective stated precisely with the correct term from the model answer (e.g. support for billions of end-systems / larger address space; reduce routing tables; simplified header; increased security; real-time/QoS support via flow label and traffic class; multicasting; mobility/roaming; extensibility via extension headers; coexistence with existing protocols). _Partial: Objective is named but only vaguely (e.g. 'better performance') — no part marks; award half only if the idea is clearly right but lacks the key term._
- **P2** (0.25): Second distinct correct objective from the model answer list, stated precisely with the correct term. _Partial: Idea clearly right but key term missing: half._
- **P3** (0.25): Third distinct correct objective from the model answer list, stated precisely with the correct term. _Partial: Idea clearly right but key term missing: half._
- **P4** (0.25): Fourth distinct correct objective from the model answer list, stated precisely with the correct term. _Partial: Idea clearly right but key term missing: half._


## saf/IPP_6.2 (1 marks)

**Question:** What are extension headers in IPv6 and where are they located in a packet? What is the main advantage of extension headers compared to IPv4?

**Model answer:** Extension headers are used to extend the fixed IPv6 header with additional, optional network layer information. If present, they are located between the fixed header/main header and payload/upper-layer header/ transport-layer header. Main advantage: One of the following advantages are considered fully correct: 1. It allows the appending of new options without changing the header. 2. IPv6 packets with optional headers are typically processed faster/simpler by intermediate devices as most of the options are ignored (except “Hop-by-Hop Extension”) while they are processed by all routers in IPv4 unless ordered otherwise.

_Marking stance: harsh. Full marks need all four elements stated precisely: what extension headers are, where they sit (between fixed header and payload/upper-layer header), a valid advantage, and its specific reason or IPv4 contrast. Vague answers such as 'more flexible' or 'better' earn nothing for the advantage points. A wrong statement within a point (for example placing them after the payload or before the fixed header) cancels that point._

- **P1** (0.25): Defines extension headers precisely: they extend the fixed (main) IPv6 header with additional, optional network-layer information/options.
- **P2** (0.25): Location: if present, they are placed between the fixed/main IPv6 header and the payload (upper-layer/transport-layer header). Both boundaries must be stated. _Partial: Only one boundary or 'after the main header' stated correctly: no credit unless the payload side is also given._
- **P3** (0.25): States one valid main advantage over IPv4: (a) new options can be appended/added without changing the (fixed) header, or (b) packets with extension headers are processed faster/simpler by intermediate devices because most options are ignored by routers (except Hop-by-Hop), whereas IPv4 routers process all options unless ordered otherwise.
- **P4** (0.25): The advantage is stated precisely with its reason and IPv4 contrast: for (a) the fixed header stays unchanged/no redesign; for (b) both that intermediate routers ignore most extension headers (Hop-by-Hop exception) and that IPv4 routers process all options. A vague claim like 'more flexible' or 'more efficient' earns nothing. _Partial: Half marks if only the reason or only the IPv4 contrast is given precisely._


## saf/IPP_6.3 (1 marks)

**Question:** What is the “Dynamic Host Configuration Protocol (DHCP)”? What is it used for?

**Model answer:** The Dynamic Host Configuration Protocol (DHCP) is a network management protocol used in Internet Protocol (IP) networks, whereby a DHCP server dynamically assigns an IP address and other network configuration parameters to each device on the network. Further, DHCP has largely replaced RARP (and BOOTP) Uses of DHCP are: Simplifies installation and configuration of end systems. Allows for manual and automatic IP address assignment. May provide additional configuration information (DNS server, netmask, default router, etc.)

_Marking stance: harsh. Full marks need every element stated precisely with correct terms: DHCP as an IP network management protocol, a DHCP server dynamically assigning IP addresses, other parameters (DNS server, netmask, default router), and the uses (simpler end-system configuration, manual and automatic assignment). Give part marks only if clearly more than half of a point is stated. Vague statements such as 'it gives IPs' earn nothing for the detailed points, and any wrong detail (for example saying DHCP maps IP to MAC like ARP) cancels that point. Mentioning that DHCP replaced RARP/BOOTP is optional and gains no marks._

- **P1** (0.25): Defines DHCP as a network management protocol used in IP networks (Dynamic Host Configuration Protocol), stating both that it is a network management/configuration protocol and that it is used in IP networks. _Partial: Only one of 'network management protocol' or 'IP networks' stated precisely: half._
- **P2** (0.25): States that a DHCP server dynamically assigns an IP address to each device (host) on the network, naming the DHCP server as the assigning entity. _Partial: IP address assignment stated without naming the DHCP server or without 'dynamically': half._
- **P3** (0.25): States that DHCP also provides other network configuration parameters, with correct examples such as DNS server, netmask, default router (gateway). _Partial: Says 'other configuration parameters' with only one correct example, or examples without saying it is additional: half._
- **P4** (0.25): Uses: simplifies installation/configuration of end systems AND allows both manual and automatic IP address assignment (both must be stated). _Partial: Only one of the two uses (simplified configuration, or manual and automatic assignment) stated precisely: half._


## saf/LM_2.1 (1 marks)

**Question:** What is "frame bursting"? Also, give 1 advantage and disadvantage compared to the carrier extension.

**Model answer:** Frame bursting reduces the overhead for transmitting small frames by concatenating a sequence of multiple frames in one single transmission, without ever releasing control of the channel. Advantage :it is more efficient than carrier extension as single frames not filled up with garbage. Disadvantage :need frames waiting for transmission or buffering and delay of frames

_Marking stance: harsh. Full marks need the precise definition (multiple frames concatenated in one transmission without releasing the channel), the small-frame overhead purpose, and one correct advantage and one correct disadvantage versus carrier extension. A vague statement such as 'sends frames faster' earns nothing for that point. A wrong advantage or disadvantage (e.g. claiming it pads frames) earns nothing for that point._

- **P1** (0.4): Defines frame bursting as concatenating/sending a sequence of multiple frames in one single transmission (burst), WITHOUT releasing control of the channel in between. _Partial: Half (0.2) if only says multiple frames are sent together but omits keeping control of the channel (or vice versa)._
- **P2** (0.15): States that its purpose is to reduce the overhead of transmitting small frames.
- **P3** (0.225): Advantage vs carrier extension: more efficient because single small frames are not padded/filled with extension (garbage) bits, so no wasted bandwidth. _Partial: Half if says only 'more efficient' without linking to no padding of frames._
- **P4** (0.225): Disadvantage vs carrier extension: needs frames queued/waiting for transmission (buffering), causing delay of frames. _Partial: Half if only buffering/waiting frames or only delay is stated, not both._


## saf/LM_4.1 (1 marks)

**Question:** What happens to the "collision domain diameter" if you use CSMA / CD and increase the speed of a network by a factor of 10, eg from 10Mb / s to 100Mb / s (all else being equal)?

**Model answer:** Diameter decreases by a factor of 10, e.g 300m to 30m.

_Marking stance: harsh. Full marks need both the direction (decreases) and the exact factor (10, or e.g. 300 m to 30 m). Saying only 'it gets smaller' earns 0.5. Any wrong direction or wrong factor (e.g. 'increases', 'halves') earns nothing for that point; a wrong example figure inconsistent with a factor of 10 cancels P2._

- **P1** (0.5): States that the collision domain diameter decreases (gets smaller / shrinks), not increases or stays the same.
- **P2** (0.5): States the decrease is by a factor of 10 (diameter becomes one tenth), e.g. about 300 m to 30 m. A wrong factor or wrong example figures cancel this point. _Partial: Factor of 10 implied only via a correct example (e.g. 300m to 30m) without stating the factor explicitly: half of this point_


## saf/MM_8.1 (1 marks)

**Question:** WHAT are the challenges of Mobile Routing compared to routing in fixed and wired networks? Please NAME and DESCRIBE two challenges.

**Model answer:** Possible Challenges: 1.Adaptation: The network has to handle the dynamic positioning of the nodes/topology changes. Additionally, nodes can leave or join the network anywhere (within signal range) at any time. 2.Security: Interception of packets or injection of faulty packages is easily possible in wireless networks. This may necessitate encryption and authentication. 3.Medium Access Control: Wireless networks feature new possibilities for inference and collisions of the transmitted signals. See the following correct example challenges: i)Hidden Terminal: Nodes’ transmissions may collide at other nodes without them noticing, because they are out of detection range of each other (A and C in this example) and therefore sense the medium to be free even though there is an overlap of the transmission ranges. ii)Exposed Terminal: Nodes (C in this example) may not realize they could send collision-free, because a node in their detection range (B) is sending and they, therefore, detect the medium as busy, but the sending node (B) is out of the detection range of the destination node (D) so that no collision would occur. iii)Near and Far Terminals: Signal strength decreases proportionally to the square of distance, so closer nodes may drown out the weaker signals of nodes farther away. 4.Quality of Service (QoS): Due to the rapidly changing network topology, imprecise network information, and resource constraints of participating nodes, it is challenging to provide the desired QoS. Additionally, signal quality may also decline due to noise and occlusion. 5.Scalability: Since it is not possible to know the number of participating nodes beforehand, it is vital that routing protocols, etc. are capable of dealing with increasing network sizes and workloads. 6.Heterogeneity: Nodes may have different capabilities, responsibilities, and constraints, e.g. processing capacity, transmission ranges 7.Dependability: Providing consistent, performant, and reliable routing behavior that higher-level services can trust is challenging in such a dynamic environment. 8.Power Consumption: As most mobile devices are battery-powered, power consumption becomes an important optimization factor in routing, etc.

_Marking stance: harsh. Full marks need two distinct challenges from the model answer's list, each named with the correct term and described with the specific details. A vague name without a description, or a generic description such as "it is harder in wireless" earns nothing for that point. A wrong detail in a description cancels that description's mark. A challenge that is not in the model answer, or is only a repeat of the first, earns nothing. Do not pay a description unless the matching name is given or clearly identified._

- **P1** (0.25): First challenge is correctly named using a valid term from the model answer (e.g. Adaptation/topology changes, Security, Medium Access Control (hidden/exposed/near-far terminal), QoS, Scalability, Heterogeneity, Dependability, Power Consumption).
- **P2** (0.25): First challenge is described precisely and correctly, matching the model answer's specific content (e.g. for Adaptation: nodes move and topology changes dynamically, nodes can join or leave anywhere at any time; for Security: packets can be intercepted or faulty packets injected, needing encryption/authentication; for MAC: interference/collisions, e.g. hidden terminal; for Power: battery-powered devices so energy must be optimised). _Partial: Half (0.125) if the description gives clearly more than half of the required detail, e.g. only one of the two aspects._
- **P3** (0.25): Second, different challenge is correctly named using a valid term from the model answer.
- **P4** (0.25): Second challenge is described precisely and correctly, matching the model answer's specific content for that challenge. _Partial: Half (0.125) if the description gives clearly more than half of the required detail._


## saf/MM_8.2 (1 marks)

**Question:** WHAT is the purpose of Reverse Path Forwarding and Reverse Path Broadcast? HOW do they work?

**Model answer:** Purpose: Both implement a more efficient kind (in terms of duplicate packets) of broadcasting than flooding / to minimize the number of duplicate packets in the network when broadcasting. Reverse Path Forwarding: Each node has a routing table stemming from unicast routing algorithms. When receiving a packet of sender S from neighbor N at node X, check the routing table and only forward the packet to all adjacent nodes (except for N) when you would send packets to S over N → the assumption is that the packet used the BEST route until now. Reverse Path Broadcast: Nodes monitor unicast traffic to learn which paths in the network they are a part of, that is node X knows that is on the best path between two nodes A and B if it receives unicast packets coming from A and going to B or visa versa. In other words, each node knows which spanning trees it is part of in the network. Reverse Path Broadcasting works identical to Reverse Path Forwarding with the exception that it only forwards packets on edges that are part of a spanning tree (again excluding the incoming line to N).

_Marking stance: harsh. Full marks need every element stated precisely with correct terms: duplicate-packet reduction versus flooding, the RPF routing-table check via the incoming neighbour N, the forward-to-all-except-N rule, RPB's learning from unicast traffic, and forwarding only on spanning-tree edges. Give part marks only where clearly more than half of a point is precise. A wrong statement (e.g. RPF forwards when the packet did not come from the best route, or RPB uses no spanning tree) or vague generic wording earns nothing for that point._

- **P1** (0.2): Purpose: both RPF and RPB implement broadcasting that is more efficient than flooding, i.e. they minimise the number of duplicate packets in the network during broadcast. _Partial: Half if only says 'broadcast' or 'efficient' without reference to reducing duplicate packets / improvement over flooding._
- **P2** (0.25): RPF basis: each node uses its routing table from unicast routing algorithms; on receiving a packet from sender S via neighbour N at node X, X checks the routing table for the route to S. _Partial: Half if routing table is mentioned but the check of the route towards source S via incoming neighbour N is not stated._
- **P3** (0.25): RPF forwarding rule: X forwards the packet to all adjacent nodes except N only if it would itself send packets to S via N (packet arrived on the best/shortest path); otherwise it discards it. Assumption: the packet has used the best route so far. _Partial: Half if only the forward-if-from-best-path condition is stated, without excluding N or the discard/assumption._
- **P4** (0.15): RPB learning: nodes monitor unicast traffic to learn which paths they lie on; node X knows it is on the best path between A and B if it sees unicast packets from A to B (or vice versa), so each node knows which spanning trees it is part of. _Partial: Half if only says nodes learn spanning-tree membership without stating that it is by observing unicast traffic._
- **P5** (0.15): RPB forwarding: works identically to RPF, except that it forwards packets only on edges that are part of a spanning tree (still excluding the incoming line N). _Partial: Half if says it restricts forwarding to spanning-tree edges but not that the rest is the same as RPF/excludes N._


## saf/MM_8.3 (1 marks)

**Question:** WHICH PROPERTY of spanning trees makes them appealing for broad- and multicasting? EXPLAIN how you can modify Link State Routing to construct a spanning tree for multicasting.

**Model answer:** Property: There is a single unique path between every pair of nodes in the tree. Alternatively, you can say that spanning trees are subnets of a network that do not contain loops but contain all nodes. This means that no unnecessary duplicates are distributed in the network when forwarding packets using that tree structure. Spanning Tree with Link State Routing: Each intermediate system knows which multicast groups it belongs to, but initially doesn’t know which other IS belong to the groups. Therefore, you can add multicast group information to the link state packet and each node can construct multicast trees once the full network topology and group information are distributed in the whole network, as each node then has the complete state information stored locally (e.g. with Prim or Kruskal)

_Marking stance: harsh. Full marks need all four elements stated precisely: the unique-path/loop-free property, the no-duplicates reason, multicast group info added to link state packets and distributed, and local tree computation (Prim/Kruskal) from complete information. Vague statements such as "it is efficient" or "use link state routing" earn nothing for the point. A wrong statement within a point (e.g. the tree contains loops, or the tree is computed centrally) cancels that point._

- **P1** (0.25): States the property: there is a single unique path between every pair of nodes (equivalently: loop-free subnet containing all nodes).
- **P2** (0.25): Explains why this suits broad/multicasting: no loops, so no unnecessary duplicate packets are distributed when forwarding along the tree.
- **P3** (0.25): Modification: each intermediate system/node adds its multicast group membership information to its link state packet, which is distributed network-wide (because a node initially only knows its own groups). _Partial: Half if only says group information is added to LSPs but not that it is flooded/distributed to all nodes or why._
- **P4** (0.25): Once the full topology and group information are known locally at every node, each node computes the multicast spanning tree itself using a spanning tree algorithm such as Prim or Kruskal. _Partial: Half if says each node computes the tree locally from complete information but names no algorithm or gives a wrong one._


## saf/PE_12.1 (1 marks)

**Question:** Let us assume that you flip a coin 6 times where the probability of heads (H) showing up is 0.6. Please arrange the following events in the increasing order of their likelihood (i.e., least probable → most probable): ● Event A: you see at least three H’s ● Event B: you see the sequence HHHTTT ● Event C: you see exactly three H’s Include justification in your answer headers.

**Model answer:** The correct sequence is BCA , where B is the least probable. One of the following justifications should be given: ● Event B is a subset/part/special case of C, and C is a subset/part/special case of A ● Event B is more specific/strict than C and C is more specific/strict than A ● An actual, correct calculation of the probabilities: ○ P(B) = 0.6 * 0.6 * 0.6 * 0.4 * 0.4 *0.4 = 0.6^3 *0.4^3 = 0.013824 ○ P(C) = (6 choose 3) * P(B) = 0.27648 ○ P(A) = P(C) + P(Y=4) + P(Y=5) + P(Y=6) = 1 - P(Y=0) - P(Y=1) - P(Y=2) = (6 choose 3) * 0.6^3 * 0.4^3 + (6 choose 4) * 0.6^4 * 0.4^2 +(6 choose 5) * 0.6^5 * 0.4 + (6 choose 6) * 0.6^6 = 0.27648 + 15 * 0.020736 + 6 * 0.031104 + 1 * 0.046656 = 0.8208 ○ The answer may be rounded to up to 2 decimal places, e.g. P(B) = 0.01 or P(B) = 0.014 ○ It is also sufficient to give a formula without the actual calculation, if it is apparent that P(B) less than P(C) less than P(A), e.g. by stating P(C) = 20 * P(B)

_Marking stance: harsh. Full marks need the order BCA stated correctly and a justification covering both B<C and C<A, using subset/specificity reasoning or correct calculations. A wrong order earns nothing for P1, and any wrong probability value or incorrect claim in the justification cancels P2. A justification for only one comparison earns 0.25; a bare order with no justification earns only P1._

- **P1** (0.5): States the correct order explicitly: B, then C, then A (B least probable, A most probable), i.e. B < C < A.
- **P2** (0.5): Gives a valid justification covering both comparisons (B below C AND C below A): either B is a subset/special case/more specific than C and C is a subset/special case/more specific than A; or correct probabilities/formulas, e.g. P(B)=0.6^3*0.4^3≈0.0138, P(C)=C(6,3)*P(B)≈0.276, P(A)≈0.82 (rounding to 2 d.p. allowed; formula such as P(C)=20*P(B) is enough if the ordering is apparent). _Partial: Only 0.25 if the justification is correct for just one of the two comparisons (B vs C or C vs A) and contains no errors._


## saf/PE_12.2 (1 marks)

**Question:** Consider a single server queueing system with a buffer of size 10. Let us assume that 9 packets arrive per second and 10 packets are served per second on an average. Assume you monitor the system for exactly one minute after the system reaches equilibrium. How many seconds would you expect the system to be in a state in which there are less than 10 packets waiting in the queue? You need to justify your answer by showing steps involved; calculations, however, need not be included. headers.

**Model answer:** Since we have a buffer size (N) of 10, we will always have less than 10 packets waiting in the queue unless there are exactly 10 packets in the queue. Therefore, we first calculate the probability of the system being full/having 10 packets in the queue. This is also called “blocking probability” or P_B. P_B = ((1 - utilization) * utilization^N) / 1 - utilization^(N+1) = ((1-0.9) * 0.9^10) / (1 - 0.9^11) = 0.0508 Alternatively to the blocking probability, it is also valid to directly calculate P(X less than 10) = (1 -P_B) by summing up the probabilities for 0, 1, …, 9 packets to be in the queue. To calculate the expected time where the system is not blocked in the 60-second observation time-frame, we simply multiply the time frame with P(X less than 10) or the complement of P_B (0.25p) = 60 * (1-P_B) = 56.9512 seconds

_Marking stance: harsh. Full marks need all four steps stated precisely: complement of the full state, correct M/M/1/N formula with ρ=0.9 and N=10, P_B≈0.0508, and 60×(1−P_B)≈56.95 s. A wrong detail (e.g. using M/M/1 without finite buffer, wrong N, or wrong ρ) cancels that point and usually the later ones. A bare final number or vague statement without the method earns nothing for the steps it skips; summing P(0..9) directly is accepted as an alternative._

- **P1** (0.25): Identifies that fewer than 10 packets in the queue is the complement of the system being full (exactly N = 10 packets, buffer full), i.e. the answer needs the blocking probability P_B (or directly P(X<10) = sum of state probabilities for 0..9).
- **P2** (0.25): States the correct M/M/1/N blocking probability formula with utilization ρ = λ/μ = 9/10 = 0.9 and N = 10: P_B = ((1-ρ)ρ^N)/(1-ρ^(N+1)). _Partial: Formula correct but ρ not identified as 0.9 (or vice versa), give half._
- **P3** (0.25): Computes P_B ≈ 0.0508 (or equivalently P(X<10) ≈ 0.949) correctly.
- **P4** (0.25): Multiplies the 60 s observation time by P(X<10) = 1 - P_B and gives the final answer ≈ 56.95 s (about 57 s).


## saf/PE_12.3 (1 marks)

**Question:** To model the packet arrivals as a poisson process, we assumed that the arrivals for each time interval Δt are independent. Does this assumption hold for real INTERNET traffic? Explain your answer in 2-5 sentences.

**Model answer:** No. Real internet traffic often comes in bursts. Therefore, arrivals are not independent because the probability of an arrival happening at a node is influenced by previous arrivals at the node. For example, on-demand video streams selectively load the next video segments when needed. This means the actual network utilization depends on the current playback state on the client-side. The packet arrivals are not independent, as it is likely that there is a low utilization directly after the next segments have been loaded.

_Marking stance: harsh. Full marks need a clear "No", burstiness, the explanation that arrival probability depends on previous arrivals, and a correct specific example with its mechanism. Each point is all or nothing except the example, which gets half only if the example is named without its mechanism. A generic statement such as "traffic is not random" or a wrong claim (e.g. that the assumption holds) earns nothing for that point._

- **P1** (0.25): States clearly that the assumption does NOT hold for real internet traffic (arrivals in different intervals are not independent).
- **P2** (0.25): States that real internet traffic is bursty (arrives in bursts).
- **P3** (0.25): Explains the dependence precisely: the probability of an arrival at a node is influenced by previous arrivals at that node (arrivals are correlated over time).
- **P4** (0.25): Gives a correct specific example, e.g. on-demand video streaming loads the next segments only when needed, so utilization depends on client playback state and is low right after segments have been loaded. _Partial: Names streaming/video as an example but does not explain the dependence on playback state or low utilization after loading._


## saf/SDN_11.1 (1 marks)

**Question:** Software-defined Networking (SDN) introduces separate control and data planes to manage network flows. Please explain the responsibilities of each plane in 1-2 sentences. Further, name two tasks the SDN controller takes care of.

**Model answer:** Control Plane: The control plane is logically centralized, but can be physically distributed (multiple coordinating control servers for higher availability and scalability). One of the following responsibilities should be given: ● decides the route for the packet/data ○ Control servers manage the network graph, define routes, and update the flow tables of connected switches. ● handles unprocessed packets coming in from the data plane Data plane: Responsible for packet forwarding. Individual switches just execute actions according to their flow tables decided upon by the control plane. The following are the tasks taken care of by the controller: ● Configuration of forwarding tables ● Injecting packets ● Events from switch (packet-in) ● Collection/Monitoring of traffic statistics ● Discovery of topology ● Inventorying what devices are within the network and the capabilities of each device ● Interfaces with control logic (control “application”) via the northbound interface(s) ● Implements a southbound interface to interact with the data plane. ● Implements the control plane.

_Marking stance: harsh. Full marks need a precise control plane responsibility, a precise data plane responsibility (forwarding per flow tables), and two distinct, correct controller tasks from the model list. Vague statements like 'controls the network' earn nothing for that point. A wrong statement within a point (e.g. data plane makes routing decisions) cancels that point; a wrong extra controller task cancels its point. Repeating the same task twice earns only one point._

- **P1** (0.25): Control plane responsibility stated precisely: it decides the routes/forwarding of packets (manages network graph, defines routes, updates switches' flow tables) OR handles unprocessed packets coming from the data plane; and it is logically centralized (may be physically distributed). _Partial: Half (0.125) if a correct responsibility is given but without mention of logical centralization/flow-table control, or vice versa._
- **P2** (0.25): Data plane responsibility stated precisely: it is responsible for packet forwarding; switches just execute actions according to their flow tables as decided by the control plane. _Partial: Half (0.125) if only 'forwards packets' is stated without that switches follow flow tables set by the control plane._
- **P3** (0.25): First controller task named correctly and specifically, from the model list (e.g. configuring forwarding/flow tables, injecting packets, handling packet-in events, collecting traffic statistics, topology discovery, device inventory, northbound/southbound interfaces, implementing the control plane).
- **P4** (0.25): Second, different controller task named correctly and specifically, from the model list.


## saf/SDN_11.2 (1 marks)

**Question:** What are the benefits and drawbacks of SDN compared to traditional networking,where each switch/router has to manage forwarding and routing on its own? Describe two benefits and two drawbacks in 1-2 sentences each.

**Model answer:** Benefits: ● Reduced complexity of the switches: They only have to act according to their flow tables and do not have to make any local routing decisions. ● Due to centralized routing, the routing can converge way faster to a global optimum than with decentralized routing because of a global view ● Better Integration of application and network provides a better global view of the system. ● Increased flexibility : 1. We can update the routing logic on the fly, routers/switches are not limited to hard-coded routing algorithms anymore (Note: this is also possible with programmable switches). 2. API to “program” the network: Software (application) “defines” the network 3. High-level programming languages for implementation of logic and making use of powerful integrated development environments. Note: In case the reasoning/example sufficiently explains the benefit, naming like reduced complexity, increased flexibility can be omitted and response can still be granted 0.25 for each benefit. Drawbacks: ● High complexity of the control servers: They have to make all the routing decisions for the (sub)network and can therefore be a bottleneck. ● Centralized routing in distributed systems in general: The routing completely depends on the control server(s). To achieve better availability and fault tolerance, the number of control servers can be increased. However, this can lead to synchronization and consistency issues. → CAP problem (consistency, availability, partition tolerance) ● New technology adoption challenges: ● Switching to SDN from traditional networking. ● Training personnel on SDN. All these will cost depending on the reconfiguration level but then for the long term, it depends upon the ROI. ● Security-related concerns : ○ Lack of hardware security: eliminating the use of the physical routers and switches, one also loses the security that comes with it.

_Marking stance: harsh. Full marks need exactly two distinct benefits and two distinct drawbacks from the model answer, each with both the item and its reason. A bare label or a generic claim like "SDN is better/easier" earns nothing for that point; a named item with weak explanation earns half. A wrong statement within a point (e.g. listing a drawback as a benefit, or saying switches make routing decisions in SDN) cancels that point; do not credit benefits or drawbacks beyond two per category._

- **P1** (0.25): First benefit correctly named/identified AND explained with its reason, e.g. reduced switch complexity (switches only follow flow tables, no local routing decisions); or faster convergence to global optimum via centralized global view; or better application/network integration; or increased flexibility (routing logic updatable on the fly, programmable via API/high-level languages). _Partial: Benefit named correctly but reason/explanation missing or vague (or only reason without clear benefit) earns half of this point._
- **P2** (0.25): Second, different benefit from the model answer's list, correctly named AND explained with its reason (must not be a restatement of P1). _Partial: Benefit named correctly but reason/explanation missing or vague earns half of this point._
- **P3** (0.25): First drawback correctly named AND explained, e.g. control server complexity/bottleneck since it makes all routing decisions; centralized control as single point of failure with replication causing synchronization/consistency issues (CAP); adoption challenges (migration cost, personnel training, ROI); security concerns (loss of hardware security of physical routers/switches). _Partial: Drawback named correctly but reason/explanation missing or vague earns half of this point._
- **P4** (0.25): Second, different drawback from the model answer's list, correctly named AND explained (must not be a restatement of P3). _Partial: Drawback named correctly but reason/explanation missing or vague earns half of this point._


## saf/SDN_11.3 (1 marks)

**Question:** Name the two modes of control plane distribution and name one downside for each of them.

**Model answer:** Two modes of physical distribution of control plane and associated drawbacks are: Replication ● Issue of scalability ● More resources, more cost ● Wastage of resources as the replicated node is on standby and no actual load distribution occurs. ● The problem to keep the data consistent in the replicated node is hard and complex. Partitioning ● Raises issues similar to P2P networks ● Knowledge about neighborhood ● Coordination and consistency ● Lower availability

_Marking stance: harsh. Each mode must be named with the exact term (replication, partitioning) and paired with its own correct downside from the model answer. A downside given without the mode named, or attached to the wrong mode, earns nothing for that point. Vague drawbacks (e.g. "it is complex" or "costly" with no link to the mode) earn nothing; a wrong extra claim cancels that point. No part marks are needed beyond the quarter-mark steps._

- **P1** (0.25): Names Replication as one mode of control plane (physical) distribution.
- **P2** (0.25): States a correct downside of replication: scalability issue, higher resources/cost, wasted standby resources with no load distribution, or hard/complex data consistency between replicas.
- **P3** (0.25): Names Partitioning as the other mode of control plane (physical) distribution.
- **P4** (0.25): States a correct downside of partitioning: issues like P2P networks, need for knowledge of neighborhood, coordination and consistency problems, or lower availability.


## saf/SDN_11.4 (1 marks)

**Question:** In an SDN, switches maintain a pipeline of flow tables and a meter table. Summarize their respective functions in one sentence each.

**Model answer:** Meter table: collects flow statistics or contains meter entry per flow (0.25) which is taken into account by the controller for management of the network like QoS operation(rate-limiting being one of them). Flow pipeline: consists of flow tables that contain “rules” or fields (0.25) for packet forwarding(0.25) /actions to be taken on the packets or in other words it implements the routing logic in the switch

_Marking stance: harsh. Full marks need both tables covered, each with what it holds and what it is used for, using correct terms (meter entry per flow, QoS/rate-limiting, flow tables with rules, packet forwarding/actions). Give nothing for vague statements like 'meter table manages traffic' or 'flow table stores data'. Swapping the functions of the two tables, or a wrong detail in a point, earns nothing for that point._

- **P1** (0.25): Meter table function: states that it holds per-flow meter entries / collects flow statistics (per-flow meter entries must be mentioned).
- **P2** (0.25): Meter table purpose: states that these meters are used by the controller to manage the network, specifically QoS operations such as rate-limiting. _Partial: Mentions network management/QoS or rate-limiting but not both the controller use and QoS/rate-limiting._
- **P3** (0.25): Flow pipeline function: states that it consists of flow tables containing rules/fields (match fields and actions) for packets.
- **P4** (0.25): Flow pipeline purpose: states that the rules are used for packet forwarding / actions taken on packets, i.e. it implements the routing/forwarding logic in the switch.


## saf/TC_10.1 (1 marks)

**Question:** State at least 4 of the differences shown in the lecture between the UDP and TCP headers.

**Model answer:** Possible Differences : The UPD header (8 bytes) is much shorter than the TCP header (20-60 bytes) The UDP header has a fixed length while the TCP header has a variable length Fields contained in the TCP header and not the UDP header : -Sequence number -Acknowledgment number -Reserved -Flags/Control bits -Advertised window -Urgent Pointer -Options + Padding if the options are UDP includes the packet length (data + header) while TCP has the header length/data offset (just header) field instead The sender port field is optional in UDP, while the source port in TCP is necessary to establish the connection

_Marking stance: harsh. Each of four distinct, correct differences earns 0.25; the student must give at least four. Naming a TCP-only field counts as one difference per field only if it is a real field in the model answer (e.g. sequence number, window); vague statements like "TCP has more fields" earn nothing. A wrong claim (e.g. UDP has a sequence number, wrong header sizes) cancels that point. Repeating the same difference in different words counts once._

- **P1** (0.25): First valid difference stated precisely and correctly, with the correct technical terms (e.g. UDP header is 8 bytes / short and fixed-length, while TCP header is 20-60 bytes / variable-length).
- **P2** (0.25): Second distinct valid difference stated precisely and correctly. Valid differences: UDP fixed vs TCP variable header length; TCP-only fields (sequence number, acknowledgment number, reserved, flags/control bits, advertised window, urgent pointer, options + padding); UDP has a packet length field (header + data) while TCP has header length/data offset (header only); source port optional in UDP but necessary in TCP.
- **P3** (0.25): Third distinct valid difference stated precisely and correctly, using the correct field names.
- **P4** (0.25): Fourth distinct valid difference stated precisely and correctly, using the correct field names. No wrong statements among the four.


## saf/TC_10.2 (1 marks)

**Question:** In the lecture you have learned about congestion control with TCP. Name the 2 phases of congestion control and explain how the Congestion Window (cwnd) and the Slow Start Threshold (ss_thresh) change in each phase (after initialization, where cwnd = 1 and ss_thresh = advertised window size) in 1-4 sentences .

**Model answer:** Slow start (cwnd less than ss_thresh): In the slow start phase, cwnd is incremented by one every time a segment is acknowledged. This results in an exponential growth as cwnd is essentially doubled after each Round Trip Time (RTT). This is done until either a packet is lost or ss_thresh is reached. When cwnd >= ss_thresh, the congestion avoidance phase is entered. After a packet is lost / congestion the following adaption is made in both phases: ss_thresh = cwnd / 2. Then cwnd is reset to 1. Congestion Avoidance (cwnd >= ss_thresh):: In the congestion avoidance phase, cwnd is incremented more slowly. There are different incrementation strategies, but they usually grow linearly, e.g. only increment cwnd by 1 after all sent segments have been acknowledged. This is done until a packet is lost. Typically, this means that cwnd less than ss_thresh and the slow start phase is entered again. After a packet is lost / congestion the following adaption is made in both phases: ss_thresh = cwnd / 2. Then cwnd is reset to 1.

_Marking stance: harsh. Full marks need both phase names and precise cwnd/ss_thresh behaviour: +1 per ACK/exponential in slow start, linear (+1 per RTT) in congestion avoidance, and on loss ss_thresh = cwnd/2 and cwnd = 1. Vague statements such as 'grows faster' or 'cwnd is reduced' earn nothing; give part marks only where clearly more than half is precise. A wrong detail (e.g. cwnd halved instead of reset to 1, or wrong phase growth) cancels that point._

- **P1** (0.2): Names both phases correctly: Slow Start and Congestion Avoidance (both required, correct terms).
- **P2** (0.25): Slow start: cwnd increases by 1 per acknowledged segment, giving exponential growth (doubling each RTT), while cwnd < ss_thresh; ss_thresh is unchanged during growth. _Partial: 0.125 if only exponential growth/doubling per RTT is stated without the per-ACK +1 rule (or vice versa)_
- **P3** (0.25): Congestion avoidance (cwnd >= ss_thresh): cwnd grows slowly/linearly, e.g. +1 per RTT once all sent segments are acknowledged; ss_thresh unchanged during growth. _Partial: 0.125 if only 'slower/linear growth' stated without the specific increment_
- **P4** (0.15): On packet loss/congestion (in either phase): ss_thresh is set to cwnd/2 (stated precisely).
- **P5** (0.15): On packet loss/congestion (in either phase): cwnd is reset to 1, and the phase transition is correct (slow start ends at cwnd >= ss_thresh and enters congestion avoidance; after loss, slow start is re-entered).


## saf/TC_10.3 (1 marks)

**Question:** Transparent bridges manage a bridge table for the forwarding process. Please describe what information the table holds and how it is modified during the backwards learning phase. How is the table used in the forwarding process and what is one benefit of that? Please answer the question in 2-5 sentences.

**Model answer:** 1.A mapping between destinations/stations (MACs) and outgoing LAN interfaces. 2.This table is initially empty and received packages are flooded on every line. When a bridge receives a frame (as the bridge runs in promiscuous mode it listens in on all the traffic arriving at its LAN links) with source address Q on LAN L, it adds the timestamped entry “Q can be reached over L” to the table and the next time a packet with destination Q arrives, it is forwarded on link L. The time-stamp is used to update or purge old entries. Therefore, it learns by observing the incoming traffic. 3.To do selective forwarding instead of flooding. 4.i)less duplication/unnecessary flooding is prevented. ii)less congestion. iii)better bandwidth usage than flooding.

_Marking stance: harsh. Full marks need each element stated precisely with correct terms: the address-to-interface mapping, learning from the source address of incoming frames (with empty start and timestamp), destination lookup for selective forwarding, and one benefit. A vague or generic statement (e.g. 'the table stores info about the network') earns nothing for that point. A wrong detail, such as learning from the destination address, cancels that point._

- **P1** (0.25): States that the bridge table holds a mapping between stations/destination MAC addresses and the outgoing LAN interfaces/ports (both parts: address and interface). _Partial: Half only if one side of the mapping is named precisely and the other is vague._
- **P2** (0.25): Backward learning: the table starts empty; on receiving a frame with source address Q on LAN L, the bridge adds/updates an entry 'Q reachable via L' (learning from the SOURCE address of observed incoming traffic), with a timestamp used to update or purge old entries. _Partial: Half if source-address learning from incoming frames is stated precisely but the empty start or the timestamp/aging is missing._
- **P3** (0.25): Use in forwarding: the bridge looks up the frame's destination address in the table and forwards it only on the associated link/interface (unknown destinations are flooded). _Partial: Half if lookup of destination is stated but the forwarding only on the matching link is vague._
- **P4** (0.25): Names one correct benefit: selective forwarding instead of flooding, giving less unnecessary duplication, less congestion, or better bandwidth usage.
