# saf: lenient rubrics

Marks per point add up to the question total.

## saf/DLL_2.1 (1 marks)

**Question:** Name the 3 service classes the Data Link Layer offers and explain the differences between the classes.

**Model answer:** 1.unconfirmed connectionless - no ACK, loss of data possible, no flow control, no connect or disconnect. 2.confirmed connectionless - with ACK, no loss of data (timeout and retransmit instead→ duplicates and sequence errors possible), no flow control, no connect or disconnect. 3.connection-oriented - no data loss, duplication or sequencing errors. Instead a 3 phased communication with connect and disconnect, and flow control

_Marking stance: lenient. Full marks for naming all three classes and giving the main difference for each: ACK or not, loss or not, and connection phases with flow control. Part marks for vague or incomplete differences, or for naming only some classes. No marks for wrong or missing classes with no relevant differences. Extra minor detail, such as duplicates in the confirmed class, is not needed._

- **P1** (0.34): Names the three service classes: unconfirmed connectionless, confirmed connectionless, connection-oriented (any reasonable wording). _Partial: Two of the three named, or names given without clear distinction: about half._
- **P2** (0.33): Explains the connectionless classes' difference: unconfirmed has no acknowledgement so data can be lost; confirmed uses acknowledgements (with timeout/retransmit) so data is not lost. _Partial: Mentions only ACK vs no ACK, or only loss vs no loss: about half._
- **P3** (0.33): Explains that connection-oriented differs by having connect/data transfer/disconnect phases, with flow control and reliable, ordered delivery without duplicates, unlike the connectionless classes. _Partial: Gives only one of: connection setup/release, or reliability/flow control: about half._


## saf/DLL_2.2 (1 marks)

**Question:** What is the difference between asynchronous and synchronous transmission mode in the Data Link Layer.

**Model answer:** Asynchronous transmission: Every character a self-contained unit surrounded by a start bit and a stop bit, which is an easy and cheap pattern, but causes low transmission rates. Synchronous transmission: Several characters pooled to a continuous stream of data (frames), Frames defined by SYN or flag, higher complexity, but higher transmission rates. Requires synchronization between sender and receiver.

_Marking stance: lenient. Full marks for stating the central contrast: asynchronous sends single characters with start/stop bits, synchronous sends characters pooled in frames/continuous stream with synchronization. Give part marks for vague or one-sided answers (e.g., only describing one mode, or only saying one is faster). Wrong extra remarks do not cost marks unless they swap the two modes._

- **P1** (0.5): Asynchronous transmission: each character is sent as its own unit, framed by a start bit and a stop bit (simple/cheap, lower transmission rate). _Partial: Half if only says characters are sent individually or only mentions start/stop bits without a clear contrast, or just says it is slower/simple._
- **P2** (0.5): Synchronous transmission: many characters grouped into a continuous stream/frames (delimited by SYN or flag), needing sender–receiver synchronization, more complex but higher transmission rate. _Partial: Half if only says data is sent in blocks/frames or only says it is faster/needs synchronization, without the fuller idea._


## saf/DLL_2.3 (1 marks)

**Question:** What requirement has to be met so that you can use the piggybacking extension to the sliding window protocol?

**Model answer:** Piggybacking only makes sense if there is a full-duplex or semi-duplex connection between sender and receiver i.e. two-way communication or Frames must contain additional field for acknowledgement.

_Marking stance: lenient. Full marks for saying the connection must be two-way (full- or semi-duplex), or that data frames need a field for acknowledgements; either wording of the central idea is enough. Part marks for vague answers such as 'both sides must send data' or 'ACK sent with data' without clearly giving the requirement. No marks for unrelated answers, e.g. one-way only transmission._

- **P1** (1): States that piggybacking requires two-way communication, i.e. a full-duplex or half/semi-duplex connection (data flowing in both directions between sender and receiver), or that frames carry an extra acknowledgement field so ACKs can ride on data frames. _Partial: Half marks if only vaguely on track, e.g. says both sides send data or mentions acknowledgements attached to data frames without stating the two-way requirement._


## saf/IPP_6.1 (1 marks)

**Question:** What are the objectives of IPv6? Please state at least 4 objectives.

**Model answer:** To support billions of end-systems. To reduce routing tables. To simplify protocol processing with Simplified header. To increase security. To support real time data traffic (quality of service). Flow label, traffic class. To provide multicasting. To support mobility (roaming). To be open for change (future): extension headers for additional change incorporation. To coexistence with existing protocols.

_Marking stance: lenient. Full marks for four or more valid objectives from the model answer, in any wording; short phrases are enough. Give part marks for fewer than four (one or two valid objectives is about 0.25; three about 0.75). Wrong extra items do not cost marks; only count correct ones._

- **P1** (0.5): States at least two valid IPv6 objectives from the model answer (e.g. support billions of end-systems/larger address space, reduce routing tables, simplified header, better security, QoS/real-time support, multicasting, mobility, extensibility via extension headers, coexistence with existing protocols). _Partial: Half marks for one valid objective._
- **P2** (0.5): States at least four valid IPv6 objectives in total (any wording, brief is fine). _Partial: Quarter mark for three valid objectives._


## saf/IPP_6.2 (1 marks)

**Question:** What are extension headers in IPv6 and where are they located in a packet? What is the main advantage of extension headers compared to IPv4?

**Model answer:** Extension headers are used to extend the fixed IPv6 header with additional, optional network layer information. If present, they are located between the fixed header/main header and payload/upper-layer header/ transport-layer header. Main advantage: One of the following advantages are considered fully correct: 1. It allows the appending of new options without changing the header. 2. IPv6 packets with optional headers are typically processed faster/simpler by intermediate devices as most of the options are ignored (except “Hop-by-Hop Extension”) while they are processed by all routers in IPv4 unless ordered otherwise.

_Marking stance: lenient. Full marks need all three parts: what they are, where they sit, and one valid advantage, in any wording. Give part marks for vague but relevant statements. Wrong extra remarks cost nothing unless they contradict a central idea. Round the total to the nearest quarter._

- **P1** (0.34): States what extension headers are: optional additional network-layer information/headers that extend the fixed (main) IPv6 header. _Partial: Vague but on track (e.g. just 'extra headers') earns about half._
- **P2** (0.33): States location: between the fixed/main IPv6 header and the payload/upper-layer (transport) header. _Partial: Says only 'after the main header' or 'before the payload' earns about half._
- **P3** (0.33): Gives one valid main advantage: new options can be added without changing the base header, OR packets with options are processed faster/simpler by intermediate routers since most extension headers are ignored (except Hop-by-Hop), unlike IPv4 where options are processed by all routers. _Partial: Vague advantage such as 'more flexible' or 'more efficient' earns about half._


## saf/IPP_6.3 (1 marks)

**Question:** What is the “Dynamic Host Configuration Protocol (DHCP)”? What is it used for?

**Model answer:** The Dynamic Host Configuration Protocol (DHCP) is a network management protocol used in Internet Protocol (IP) networks, whereby a DHCP server dynamically assigns an IP address and other network configuration parameters to each device on the network. Further, DHCP has largely replaced RARP (and BOOTP) Uses of DHCP are: Simplifies installation and configuration of end systems. Allows for manual and automatic IP address assignment. May provide additional configuration information (DNS server, netmask, default router, etc.)

_Marking stance: lenient. Full marks for saying DHCP is a protocol where a server automatically gives IP addresses (and other settings) to devices, and that it is used to ease or automate host configuration. Give part marks for vague but relevant answers, such as only saying it assigns IP addresses with no mention of use. Mentioning RARP/BOOTP or specific parameters is not required; extra remarks don't lose marks unless they contradict the main idea._

- **P1** (0.5): States what DHCP is: a network protocol in which a server dynamically assigns IP addresses (and other configuration parameters) to devices/hosts on the network. _Partial: Half if it only says it is a protocol for IP/network configuration without mentioning dynamic assignment of addresses by a server._
- **P2** (0.5): States what it is used for: simplifying/automating configuration of end systems, e.g. automatic (or manual) IP assignment and supplying extra settings such as DNS server, netmask or default router. _Partial: Half if the use is only vaguely given (e.g. 'for network setup') without the idea of automatic assignment or extra parameters._


## saf/LM_2.1 (1 marks)

**Question:** What is "frame bursting"? Also, give 1 advantage and disadvantage compared to the carrier extension.

**Model answer:** Frame bursting reduces the overhead for transmitting small frames by concatenating a sequence of multiple frames in one single transmission, without ever releasing control of the channel. Advantage :it is more efficient than carrier extension as single frames not filled up with garbage. Disadvantage :need frames waiting for transmission or buffering and delay of frames

_Marking stance: lenient. Full marks need a brief definition (multiple frames sent in one go while holding the channel), one advantage and one disadvantage, in any wording. Give part marks for vague or incomplete versions of each part. Extra wrong remarks do not cost marks unless they contradict the main idea._

- **P1** (0.4): Defines frame bursting: several frames are sent one after another in a single transmission/burst, keeping hold of the channel (no release between frames), which cuts overhead for small frames. _Partial: Half if only says multiple frames are sent together, without the channel/overhead idea._
- **P2** (0.3): Gives an advantage over carrier extension, e.g. more efficient because no padding/garbage fill is needed for each small frame. _Partial: Half if just says it is better/more efficient without a reason._
- **P3** (0.3): Gives a disadvantage compared to carrier extension, e.g. needs frames queued/buffered and waiting, which causes delay. _Partial: Half if vague, e.g. more complex, without buffering or delay._


## saf/LM_4.1 (1 marks)

**Question:** What happens to the "collision domain diameter" if you use CSMA / CD and increase the speed of a network by a factor of 10, eg from 10Mb / s to 100Mb / s (all else being equal)?

**Model answer:** Diameter decreases by a factor of 10, e.g 300m to 30m.

_Marking stance: lenient. Full marks for saying the diameter shrinks by about a factor of 10 (e.g. 300m to 30m), in any wording. Give part marks if the student says it decreases but gives no factor, or gives a vague proportional link. No marks if the student says it increases or stays the same. Extra remarks about minimum frame size or propagation time do not cost marks unless they contradict this._

- **P1** (0.5): States that the collision domain diameter decreases (gets smaller/shorter) when the speed is increased. _Partial: Half if only says it changes or is affected by speed without clear direction._
- **P2** (0.5): States the decrease is by a factor of about 10 (proportional to the speed increase), e.g. 300m to 30m. _Partial: Half if says it shrinks a lot/proportionally but gives no factor._


## saf/MM_8.1 (1 marks)

**Question:** WHAT are the challenges of Mobile Routing compared to routing in fixed and wired networks? Please NAME and DESCRIBE two challenges.

**Model answer:** Possible Challenges: 1.Adaptation: The network has to handle the dynamic positioning of the nodes/topology changes. Additionally, nodes can leave or join the network anywhere (within signal range) at any time. 2.Security: Interception of packets or injection of faulty packages is easily possible in wireless networks. This may necessitate encryption and authentication. 3.Medium Access Control: Wireless networks feature new possibilities for inference and collisions of the transmitted signals. See the following correct example challenges: i)Hidden Terminal: Nodes’ transmissions may collide at other nodes without them noticing, because they are out of detection range of each other (A and C in this example) and therefore sense the medium to be free even though there is an overlap of the transmission ranges. ii)Exposed Terminal: Nodes (C in this example) may not realize they could send collision-free, because a node in their detection range (B) is sending and they, therefore, detect the medium as busy, but the sending node (B) is out of the detection range of the destination node (D) so that no collision would occur. iii)Near and Far Terminals: Signal strength decreases proportionally to the square of distance, so closer nodes may drown out the weaker signals of nodes farther away. 4.Quality of Service (QoS): Due to the rapidly changing network topology, imprecise network information, and resource constraints of participating nodes, it is challenging to provide the desired QoS. Additionally, signal quality may also decline due to noise and occlusion. 5.Scalability: Since it is not possible to know the number of participating nodes beforehand, it is vital that routing protocols, etc. are capable of dealing with increasing network sizes and workloads. 6.Heterogeneity: Nodes may have different capabilities, responsibilities, and constraints, e.g. processing capacity, transmission ranges 7.Dependability: Providing consistent, performant, and reliable routing behavior that higher-level services can trust is challenging in such a dynamic environment. 8.Power Consumption: As most mobile devices are battery-powered, power consumption becomes an important optimization factor in routing, etc.

_Marking stance: lenient. Full marks for two distinct valid challenges (any from the model answer list), each with a name and a brief description in any wording. Give part marks for a challenge that is only named or only vaguely described, or if just one challenge is given well. No marks for challenges that are not mobile/wireless-specific (e.g. generic ones that also apply to wired networks) or for repeating the same challenge twice._

- **P1** (0.5): First challenge of mobile routing is named and described in any wording (e.g. adaptation to topology changes, security, medium access/hidden-exposed terminal, QoS, scalability, heterogeneity, dependability, power consumption), with the central idea of why it is harder than in fixed wired networks. _Partial: Half marks if only named without description, or described vaguely without naming._
- **P2** (0.5): A second, different challenge from the model answer list is named and described in any wording, with its central idea. _Partial: Half marks if only named without description, or described vaguely without naming._


## saf/MM_8.2 (1 marks)

**Question:** WHAT is the purpose of Reverse Path Forwarding and Reverse Path Broadcast? HOW do they work?

**Model answer:** Purpose: Both implement a more efficient kind (in terms of duplicate packets) of broadcasting than flooding / to minimize the number of duplicate packets in the network when broadcasting. Reverse Path Forwarding: Each node has a routing table stemming from unicast routing algorithms. When receiving a packet of sender S from neighbor N at node X, check the routing table and only forward the packet to all adjacent nodes (except for N) when you would send packets to S over N → the assumption is that the packet used the BEST route until now. Reverse Path Broadcast: Nodes monitor unicast traffic to learn which paths in the network they are a part of, that is node X knows that is on the best path between two nodes A and B if it receives unicast packets coming from A and going to B or visa versa. In other words, each node knows which spanning trees it is part of in the network. Reverse Path Broadcasting works identical to Reverse Path Forwarding with the exception that it only forwards packets on edges that are part of a spanning tree (again excluding the incoming line to N).

_Marking stance: lenient. Full marks for stating the purpose (fewer duplicates than flooding) and giving the main idea of how each method works, in any wording. Give part marks for vague but on-track answers, e.g. RPF uses the routing table to check the best path to the source, and RPB restricts forwarding to spanning-tree links. Give no marks for answers unrelated to broadcasting or duplicate reduction. Wrong extra remarks do not cost marks unless they contradict the central ideas._

- **P1** (0.25): Purpose: both are broadcast methods that reduce/avoid duplicate packets compared with plain flooding (more efficient broadcasting). _Partial: Says only that they are used for broadcasting, without mentioning fewer duplicates/efficiency._
- **P2** (0.375): Reverse Path Forwarding: a node forwards a broadcast packet (to all neighbours except the incoming one) only if it arrived from the neighbour that the node's unicast routing table would use to reach the source, i.e. the packet came along the best path; otherwise it is dropped. _Partial: Mentions checking the routing table / best path to the source but is vague about forwarding or dropping._
- **P3** (0.375): Reverse Path Broadcast: works like RPF, but nodes learn (e.g. by observing unicast traffic) which links belong to a spanning tree/best paths, and forward only on those tree edges (not back on the incoming link), reducing duplicates further. _Partial: Says it is like RPF with an extra restriction to some edges/tree, but without how this is learned or used._


## saf/MM_8.3 (1 marks)

**Question:** WHICH PROPERTY of spanning trees makes them appealing for broad- and multicasting? EXPLAIN how you can modify Link State Routing to construct a spanning tree for multicasting.

**Model answer:** Property: There is a single unique path between every pair of nodes in the tree. Alternatively, you can say that spanning trees are subnets of a network that do not contain loops but contain all nodes. This means that no unnecessary duplicates are distributed in the network when forwarding packets using that tree structure. Spanning Tree with Link State Routing: Each intermediate system knows which multicast groups it belongs to, but initially doesn’t know which other IS belong to the groups. Therefore, you can add multicast group information to the link state packet and each node can construct multicast trees once the full network topology and group information are distributed in the whole network, as each node then has the complete state information stored locally (e.g. with Prim or Kruskal)

_Marking stance: lenient. Full marks: the property (unique path / loop-free, no duplicates) plus the modification (group info in link state packets, nodes build the tree locally). Give part marks for a vague or half-complete version of either part. No marks for unrelated answers; extra wrong remarks are ignored unless they contradict the main idea. Exact terms like Prim or Kruskal are not required._

- **P1** (0.5): Names the property: a spanning tree has a single unique path between any two nodes / is loop-free while connecting all nodes, so no unnecessary duplicate packets are sent. _Partial: Half if only vaguely says it avoids loops or duplicates without the unique-path/all-nodes idea, or gives the idea but is unclear._
- **P2** (0.5): Explains the Link State modification: add multicast group membership information to the link state packets so every node learns the full topology plus group info, then each node computes the multicast tree locally (e.g. with Prim or Kruskal). _Partial: Half if only mentions adding group information to link state packets, or only computing a tree from the topology, but not both._


## saf/PE_12.1 (1 marks)

**Question:** Let us assume that you flip a coin 6 times where the probability of heads (H) showing up is 0.6. Please arrange the following events in the increasing order of their likelihood (i.e., least probable → most probable): ● Event A: you see at least three H’s ● Event B: you see the sequence HHHTTT ● Event C: you see exactly three H’s Include justification in your answer headers.

**Model answer:** The correct sequence is BCA , where B is the least probable. One of the following justifications should be given: ● Event B is a subset/part/special case of C, and C is a subset/part/special case of A ● Event B is more specific/strict than C and C is more specific/strict than A ● An actual, correct calculation of the probabilities: ○ P(B) = 0.6 * 0.6 * 0.6 * 0.4 * 0.4 *0.4 = 0.6^3 *0.4^3 = 0.013824 ○ P(C) = (6 choose 3) * P(B) = 0.27648 ○ P(A) = P(C) + P(Y=4) + P(Y=5) + P(Y=6) = 1 - P(Y=0) - P(Y=1) - P(Y=2) = (6 choose 3) * 0.6^3 * 0.4^3 + (6 choose 4) * 0.6^4 * 0.4^2 +(6 choose 5) * 0.6^5 * 0.4 + (6 choose 6) * 0.6^6 = 0.27648 + 15 * 0.020736 + 6 * 0.031104 + 1 * 0.046656 = 0.8208 ○ The answer may be rounded to up to 2 decimal places, e.g. P(B) = 0.01 or P(B) = 0.014 ○ It is also sufficient to give a formula without the actual calculation, if it is apparent that P(B) less than P(C) less than P(A), e.g. by stating P(C) = 20 * P(B)

_Marking stance: lenient. Full marks: correct order BCA plus a valid justification (subset/more-specific reasoning or correct probabilities). Part marks for an almost-correct order or a vague/partial justification. No marks for a wrong order with no valid reasoning; extra incorrect remarks that don't contradict the main idea are ignored._

- **P1** (0.5): Gives the correct order: B (least), then C, then A (most probable), i.e. BCA. _Partial: Half if the order is almost right or only partly stated (e.g. B least and A most noted but C placement unclear)._
- **P2** (0.5): Gives a valid justification in any wording: B is a special case/subset of C and C of A (more specific to less specific), OR correct probability calculations/formulas showing P(B)<P(C)<P(A), e.g. P(B)≈0.014, P(C)≈0.28, P(A)≈0.82 or P(C)=20·P(B). _Partial: Half if justification is on the right track but vague or only partly correct (e.g. only one of the two relations, or a formula without clear comparison)._


## saf/PE_12.2 (1 marks)

**Question:** Consider a single server queueing system with a buffer of size 10. Let us assume that 9 packets arrive per second and 10 packets are served per second on an average. Assume you monitor the system for exactly one minute after the system reaches equilibrium. How many seconds would you expect the system to be in a state in which there are less than 10 packets waiting in the queue? You need to justify your answer by showing steps involved; calculations, however, need not be included. headers.

**Model answer:** Since we have a buffer size (N) of 10, we will always have less than 10 packets waiting in the queue unless there are exactly 10 packets in the queue. Therefore, we first calculate the probability of the system being full/having 10 packets in the queue. This is also called “blocking probability” or P_B. P_B = ((1 - utilization) * utilization^N) / 1 - utilization^(N+1) = ((1-0.9) * 0.9^10) / (1 - 0.9^11) = 0.0508 Alternatively to the blocking probability, it is also valid to directly calculate P(X less than 10) = (1 -P_B) by summing up the probabilities for 0, 1, …, 9 packets to be in the queue. To calculate the expected time where the system is not blocked in the 60-second observation time-frame, we simply multiply the time frame with P(X less than 10) or the complement of P_B (0.25p) = 60 * (1-P_B) = 56.9512 seconds

_Marking stance: lenient. Full marks need the idea that the system is below 10 unless full (blocking probability), and that the expected time is 60 × (1 − P_B), about 57 s. Give part marks for a right-track answer that is vague or has an arithmetic slip. Give no marks for answers with no queueing-probability reasoning and no time calculation. Different wording and informal steps are fine._

- **P1** (0.5): Recognises that with buffer size 10, fewer than 10 packets are waiting in every state except the full state, so the answer is based on the probability of the system not being full (1 − blocking probability P_B, or summing probabilities of 0–9 packets), using utilization 0.9 in an M/M/1/N-type formula. _Partial: Half if the student only says to use blocking probability / state probabilities without linking it to the full state or without using utilization 0.9._
- **P2** (0.5): Multiplies the 60 s observation time by the probability of not being full (1 − P_B, with P_B about 0.05) to get about 57 seconds (56.95). _Partial: Half if the student multiplies 60 by a probability with the right idea but gets the number wrong, or gives about 57 s with little justification._


## saf/PE_12.3 (1 marks)

**Question:** To model the packet arrivals as a poisson process, we assumed that the arrivals for each time interval Δt are independent. Does this assumption hold for real INTERNET traffic? Explain your answer in 2-5 sentences.

**Model answer:** No. Real internet traffic often comes in bursts. Therefore, arrivals are not independent because the probability of an arrival happening at a node is influenced by previous arrivals at the node. For example, on-demand video streams selectively load the next video segments when needed. This means the actual network utilization depends on the current playback state on the client-side. The packet arrivals are not independent, as it is likely that there is a low utilization directly after the next segments have been loaded.

_Marking stance: lenient. Full marks: says the assumption does not hold and gives any reasonable reason such as burstiness or dependence on earlier arrivals (video streaming example is optional). Part marks: a correct 'no' with no or very vague reasoning, or a good reason without an explicit 'no'. No marks: says the assumption holds, or gives an unrelated answer._

- **P1** (0.5): States that the independence assumption does not hold for real internet traffic (traffic is bursty / arrivals are not independent). _Partial: Half if only says traffic is bursty or correlated without clearly answering no._
- **P2** (0.5): Gives a reason or example: an arrival's probability depends on previous arrivals (e.g., bursts, or video streaming loading segments so utilization is low right after a load). _Partial: Half if reason is vague, e.g., just 'traffic depends on earlier traffic' without detail._


## saf/SDN_11.1 (1 marks)

**Question:** Software-defined Networking (SDN) introduces separate control and data planes to manage network flows. Please explain the responsibilities of each plane in 1-2 sentences. Further, name two tasks the SDN controller takes care of.

**Model answer:** Control Plane: The control plane is logically centralized, but can be physically distributed (multiple coordinating control servers for higher availability and scalability). One of the following responsibilities should be given: ● decides the route for the packet/data ○ Control servers manage the network graph, define routes, and update the flow tables of connected switches. ● handles unprocessed packets coming in from the data plane Data plane: Responsible for packet forwarding. Individual switches just execute actions according to their flow tables decided upon by the control plane. The following are the tasks taken care of by the controller: ● Configuration of forwarding tables ● Injecting packets ● Events from switch (packet-in) ● Collection/Monitoring of traffic statistics ● Discovery of topology ● Inventorying what devices are within the network and the capabilities of each device ● Interfaces with control logic (control “application”) via the northbound interface(s) ● Implements a southbound interface to interact with the data plane. ● Implements the control plane.

_Marking stance: lenient. Full marks need the control plane role, the data plane role, and two controller tasks, in any wording. Give part marks for vague but on-track statements or only one controller task. Wrong extra remarks cost nothing unless they swap the roles of the planes._

- **P1** (0.34): Control plane responsibility: decides/computes routes or manages the network (logically centralized), sets up/updates flow tables of switches, or handles packets the switches cannot process. _Partial: Half if only vaguely described as 'the control/brain of the network' without a responsibility._
- **P2** (0.33): Data plane responsibility: forwards packets, with switches executing actions per their flow tables set by the control plane. _Partial: Half if only says it 'handles traffic' or 'the switches' without forwarding._
- **P3** (0.33): Names two tasks of the SDN controller, e.g. configuring forwarding/flow tables, handling packet-in events, injecting packets, monitoring traffic statistics, topology discovery, device inventory, northbound/southbound interfaces, implementing the control plane. _Partial: Half if only one valid task is named._


## saf/SDN_11.2 (1 marks)

**Question:** What are the benefits and drawbacks of SDN compared to traditional networking,where each switch/router has to manage forwarding and routing on its own? Describe two benefits and two drawbacks in 1-2 sentences each.

**Model answer:** Benefits: ● Reduced complexity of the switches: They only have to act according to their flow tables and do not have to make any local routing decisions. ● Due to centralized routing, the routing can converge way faster to a global optimum than with decentralized routing because of a global view ● Better Integration of application and network provides a better global view of the system. ● Increased flexibility : 1. We can update the routing logic on the fly, routers/switches are not limited to hard-coded routing algorithms anymore (Note: this is also possible with programmable switches). 2. API to “program” the network: Software (application) “defines” the network 3. High-level programming languages for implementation of logic and making use of powerful integrated development environments. Note: In case the reasoning/example sufficiently explains the benefit, naming like reduced complexity, increased flexibility can be omitted and response can still be granted 0.25 for each benefit. Drawbacks: ● High complexity of the control servers: They have to make all the routing decisions for the (sub)network and can therefore be a bottleneck. ● Centralized routing in distributed systems in general: The routing completely depends on the control server(s). To achieve better availability and fault tolerance, the number of control servers can be increased. However, this can lead to synchronization and consistency issues. → CAP problem (consistency, availability, partition tolerance) ● New technology adoption challenges: ● Switching to SDN from traditional networking. ● Training personnel on SDN. All these will cost depending on the reconfiguration level but then for the long term, it depends upon the ROI. ● Security-related concerns : ○ Lack of hardware security: eliminating the use of the physical routers and switches, one also loses the security that comes with it.

_Marking stance: lenient. Full marks need two valid benefits and two valid drawbacks. Each is worth 0.25, and any wording is accepted if the main idea is clear. Give part marks for vague but relevant points. Give no marks for points that are irrelevant or that contradict SDN's nature, such as saying switches make their own routing decisions as a benefit._

- **P1** (0.5): Gives two benefits of SDN over traditional networking, each with a brief reason. Acceptable benefits include simpler switches that only follow flow tables, faster convergence or better routing from a global view of the network, flexibility such as updating routing logic on the fly, or programmability through APIs and high-level languages. Each benefit is worth 0.25. _Partial: 0.25 for one valid benefit, or two benefits that are only named with no reason._
- **P2** (0.5): Gives two drawbacks of SDN, each with a brief reason. Acceptable drawbacks include a complex controller that can become a bottleneck or single point of failure, consistency or synchronization problems when several controllers are used, costs of adopting the technology and training staff, or security concerns such as the loss of hardware security. Each drawback is worth 0.25. _Partial: 0.25 for one valid drawback, or two drawbacks that are only named with no reason._


## saf/SDN_11.3 (1 marks)

**Question:** Name the two modes of control plane distribution and name one downside for each of them.

**Model answer:** Two modes of physical distribution of control plane and associated drawbacks are: Replication ● Issue of scalability ● More resources, more cost ● Wastage of resources as the replicated node is on standby and no actual load distribution occurs. ● The problem to keep the data consistent in the replicated node is hard and complex. Partitioning ● Raises issues similar to P2P networks ● Knowledge about neighborhood ● Coordination and consistency ● Lower availability

_Marking stance: lenient. Full marks: both modes (replication, partitioning) named, each with one reasonable downside from the model answer, in any wording. Give part marks if only one mode or one downside is correct, or if downsides are given vaguely. No marks for unrelated answers; extra remarks are not penalised._

- **P1** (0.5): Names the two modes of control plane distribution: replication and partitioning. _Partial: Half if only one mode is named correctly._
- **P2** (0.5): Gives one valid downside for each mode: replication (e.g. scalability issue, extra cost/resources, idle standby wastes resources, hard to keep replicas consistent); partitioning (e.g. P2P-like issues, need neighborhood knowledge, coordination/consistency problems, lower availability). _Partial: Half if a valid downside is given for only one mode._


## saf/SDN_11.4 (1 marks)

**Question:** In an SDN, switches maintain a pipeline of flow tables and a meter table. Summarize their respective functions in one sentence each.

**Model answer:** Meter table: collects flow statistics or contains meter entry per flow (0.25) which is taken into account by the controller for management of the network like QoS operation(rate-limiting being one of them). Flow pipeline: consists of flow tables that contain “rules” or fields (0.25) for packet forwarding(0.25) /actions to be taken on the packets or in other words it implements the routing logic in the switch

_Marking stance: lenient. Award full marks when both the meter table and the flow pipeline are given a correct function, in any wording. Give part marks for vague but on-track statements (e.g. meter table is about statistics or rate limiting; flow tables have rules for packets). Give nothing for a part that is missing or swapped between the two tables._

- **P1** (0.5): Meter table: states that it holds per-flow meter entries / collects flow statistics, used for monitoring and QoS-type management such as rate-limiting. _Partial: Half if only vaguely says it handles statistics or rate/QoS without clear link to flows or meters._
- **P2** (0.5): Flow pipeline: states that it is a series of flow tables holding rules/entries that decide how packets are forwarded or what actions are applied to them. _Partial: Half if only says it stores rules or does forwarding in vague terms._


## saf/TC_10.1 (1 marks)

**Question:** State at least 4 of the differences shown in the lecture between the UDP and TCP headers.

**Model answer:** Possible Differences : The UPD header (8 bytes) is much shorter than the TCP header (20-60 bytes) The UDP header has a fixed length while the TCP header has a variable length Fields contained in the TCP header and not the UDP header : -Sequence number -Acknowledgment number -Reserved -Flags/Control bits -Advertised window -Urgent Pointer -Options + Padding if the options are UDP includes the packet length (data + header) while TCP has the header length/data offset (just header) field instead The sender port field is optional in UDP, while the source port in TCP is necessary to establish the connection

_Marking stance: lenient. Full marks for four distinct valid differences in any wording; listing several TCP-only fields counts as separate differences. Give part marks (a quarter per difference) for fewer than four valid differences. No marks for statements that are not header differences or are wrong. Extra wrong remarks do not cost marks._

- **P1** (0.5): States at least two valid differences between UDP and TCP headers (e.g. UDP header is shorter/fixed 8 bytes vs TCP 20-60 bytes variable; UDP source port optional vs needed in TCP; UDP has a length field while TCP has header length/data offset). _Partial: One valid difference gives a quarter mark._
- **P2** (0.5): States at least two further valid differences, e.g. TCP-only fields such as sequence number, acknowledgment number, flags/control bits, advertised window, urgent pointer, options/padding, reserved. Together with P1, at least four distinct differences are given. _Partial: One further valid difference gives a quarter mark._


## saf/TC_10.2 (1 marks)

**Question:** In the lecture you have learned about congestion control with TCP. Name the 2 phases of congestion control and explain how the Congestion Window (cwnd) and the Slow Start Threshold (ss_thresh) change in each phase (after initialization, where cwnd = 1 and ss_thresh = advertised window size) in 1-4 sentences .

**Model answer:** Slow start (cwnd less than ss_thresh): In the slow start phase, cwnd is incremented by one every time a segment is acknowledged. This results in an exponential growth as cwnd is essentially doubled after each Round Trip Time (RTT). This is done until either a packet is lost or ss_thresh is reached. When cwnd >= ss_thresh, the congestion avoidance phase is entered. After a packet is lost / congestion the following adaption is made in both phases: ss_thresh = cwnd / 2. Then cwnd is reset to 1. Congestion Avoidance (cwnd >= ss_thresh):: In the congestion avoidance phase, cwnd is incremented more slowly. There are different incrementation strategies, but they usually grow linearly, e.g. only increment cwnd by 1 after all sent segments have been acknowledged. This is done until a packet is lost. Typically, this means that cwnd less than ss_thresh and the slow start phase is entered again. After a packet is lost / congestion the following adaption is made in both phases: ss_thresh = cwnd / 2. Then cwnd is reset to 1.

_Marking stance: lenient. Full marks need both phases (slow start, congestion avoidance) with how cwnd changes in each, plus the loss reaction (ss_thresh = cwnd/2, cwnd = 1). Informal wording is fine, such as 'doubles' or 'grows fast then slowly'. Give part marks for a correct phase with vague growth or an incomplete loss reaction. Wrong extra remarks cost nothing unless they contradict the main idea, for example swapping which phase is exponential._

- **P1** (0.4): Names slow start and describes its change: cwnd grows (increases per ACK, roughly doubling each RTT / exponentially) while cwnd is below ss_thresh, until ss_thresh is reached or a loss occurs. _Partial: Names slow start but only says cwnd increases, or describes growth without naming the phase._
- **P2** (0.4): Names congestion avoidance and describes its change: cwnd grows more slowly/linearly (e.g. +1 per RTT) once cwnd >= ss_thresh, until a loss occurs. _Partial: Names congestion avoidance but gives only vague growth, or describes slower growth without naming the phase._
- **P3** (0.2): On packet loss/congestion, ss_thresh is set to cwnd/2 and cwnd is reset to 1 (ss_thresh stays unchanged otherwise). _Partial: Gives only one of ss_thresh = cwnd/2 or cwnd reset to 1._


## saf/TC_10.3 (1 marks)

**Question:** Transparent bridges manage a bridge table for the forwarding process. Please describe what information the table holds and how it is modified during the backwards learning phase. How is the table used in the forwarding process and what is one benefit of that? Please answer the question in 2-5 sentences.

**Model answer:** 1.A mapping between destinations/stations (MACs) and outgoing LAN interfaces. 2.This table is initially empty and received packages are flooded on every line. When a bridge receives a frame (as the bridge runs in promiscuous mode it listens in on all the traffic arriving at its LAN links) with source address Q on LAN L, it adds the timestamped entry “Q can be reached over L” to the table and the next time a packet with destination Q arrives, it is forwarded on link L. The time-stamp is used to update or purge old entries. Therefore, it learns by observing the incoming traffic. 3.To do selective forwarding instead of flooding. 4.i)less duplication/unnecessary flooding is prevented. ii)less congestion. iii)better bandwidth usage than flooding.

_Marking stance: lenient. Full marks for covering all parts in any wording: table contents, learning from source addresses of incoming frames, and selective forwarding with one benefit. Give part marks for right-track but vague or incomplete parts. Give nothing for parts that are missing or wrong; extra incorrect remarks do not cost marks unless they contradict the main idea._

- **P1** (0.25): States what the table holds: a mapping of stations/destination (MAC) addresses to outgoing LAN interfaces/ports. _Partial: Half if only vaguely says it holds addresses or ports without the mapping._
- **P2** (0.5): Describes how the table is modified during backward learning: starts empty; when a frame arrives with source address Q on LAN L, the bridge adds/updates an entry 'Q reachable via L' (timestamp used to refresh/purge old entries). _Partial: Half if it only says the bridge learns from the source address of incoming frames without the entry/update detail._
- **P3** (0.25): States how the table is used in forwarding (look up destination to forward selectively on the right link instead of flooding) and gives one benefit (e.g. less unnecessary traffic/congestion, better bandwidth use). _Partial: Half if only use or only benefit is given._
