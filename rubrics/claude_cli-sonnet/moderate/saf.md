# saf: moderate rubrics

Marks per point add up to the question total.

## saf/DLL_2.1 (1 marks)

**Question:** Name the 3 service classes the Data Link Layer offers and explain the differences between the classes.

**Model answer:** 1.unconfirmed connectionless - no ACK, loss of data possible, no flow control, no connect or disconnect. 2.confirmed connectionless - with ACK, no loss of data (timeout and retransmit instead→ duplicates and sequence errors possible), no flow control, no connect or disconnect. 3.connection-oriented - no data loss, duplication or sequencing errors. Instead a 3 phased communication with connect and disconnect, and flow control

_Marking stance: moderate. Full marks need the three class names and a correct distinguishing explanation of each (ACK use, reliability, connection phases, flow control). Give part marks for names with vague or incomplete differences, or for explanations missing one key feature. A wrong statement about a class loses that class's mark only; a list of names with no differences gets about 0.25–0.5._

- **P1** (0.25): Names all three service classes: unconfirmed connectionless, confirmed connectionless, and connection-oriented. _Partial: Half if only two classes are named correctly._
- **P2** (0.25): Explains unconfirmed connectionless: no acknowledgements, data loss possible, no flow control, no connect/disconnect. _Partial: Half if only no-ACK/loss is given without other differences, or stated vaguely._
- **P3** (0.25): Explains confirmed connectionless: each frame is acknowledged, so loss is handled by timeout and retransmission (duplicates/sequence errors possible), still no flow control and no connection setup. _Partial: Half if only 'with ACK' is stated without the retransmission or the lack of connection/flow control._
- **P4** (0.25): Explains connection-oriented: no loss, duplication or sequencing errors; three phases (connect, data transfer, disconnect) with flow control. _Partial: Half if only connection setup/teardown or only reliability is given._


## saf/DLL_2.2 (1 marks)

**Question:** What is the difference between asynchronous and synchronous transmission mode in the Data Link Layer.

**Model answer:** Asynchronous transmission: Every character a self-contained unit surrounded by a start bit and a stop bit, which is an easy and cheap pattern, but causes low transmission rates. Synchronous transmission: Several characters pooled to a continuous stream of data (frames), Frames defined by SYN or flag, higher complexity, but higher transmission rates. Requires synchronization between sender and receiver.

_Marking stance: moderate. Full marks need both modes described with the contrast: async = per-character with start and stop bits (low rate); sync = frames/continuous stream of many characters, needing sender-receiver synchronization (higher rate). Give part marks when a mode is only half described or vague. A description of only one mode, or generic statements without start/stop bits or frames, earns about half at most._

- **P1** (0.5): Asynchronous transmission: each character is sent as a self-contained unit framed by a start bit and a stop bit; simple/cheap but gives low transmission rate. _Partial: Half if only start/stop bits per character are given, or only simple/low-rate stated, without the other._
- **P2** (0.5): Synchronous transmission: many characters are grouped into a continuous stream/frames (delimited by SYN or flag); sender and receiver must be synchronized; more complex but higher transmission rate. _Partial: Half if only one of these is given (e.g. frames/continuous block, or synchronization, or higher rate) without the grouping into frames._


## saf/DLL_2.3 (1 marks)

**Question:** What requirement has to be met so that you can use the piggybacking extension to the sliding window protocol?

**Model answer:** Piggybacking only makes sense if there is a full-duplex or semi-duplex connection between sender and receiver i.e. two-way communication or Frames must contain additional field for acknowledgement.

_Marking stance: moderate. Full marks for stating both: the link must be two-way (full- or semi-duplex), and frames must have an extra acknowledgement field. The model answer joins these with "or", so a student who gives either one clearly and correctly should still get a good mark; use judgement and do not give more than 1 in total. Give part marks for vague wording such as "communication in both directions" without a clear statement. No marks for unrelated requirements such as window size or timers._

- **P1** (0.5): States that the connection must be two-way communication, i.e. full-duplex or semi-duplex (data flows in both directions between sender and receiver, so each side sends data frames as well as acknowledgements). _Partial: Half if it only says data goes both ways without naming duplex, or names duplex vaguely._
- **P2** (0.5): States that data frames must contain an additional field for the acknowledgement, so an ACK can be carried inside an outgoing data frame. _Partial: Half if it says acknowledgements are attached to data frames but does not mention the extra frame field._


## saf/IPP_6.1 (1 marks)

**Question:** What are the objectives of IPv6? Please state at least 4 objectives.

**Model answer:** To support billions of end-systems. To reduce routing tables. To simplify protocol processing with Simplified header. To increase security. To support real time data traffic (quality of service). Flow label, traffic class. To provide multicasting. To support mobility (roaming). To be open for change (future): extension headers for additional change incorporation. To coexistence with existing protocols.

_Marking stance: moderate. Full marks need four distinct correct IPv6 objectives from the model answer, each stated specifically. Two or three correct objectives, or four stated vaguely, earn about half. Wrong or generic items (e.g. 'faster internet') do not count toward the four; no valid objectives earns 0._

- **P1** (0.5): Lists at least four distinct, correct objectives of IPv6 drawn from the model answer: support billions of end-systems (larger address space); reduce routing tables; simplified header / simpler processing; increased security; real-time traffic / QoS (flow label, traffic class); multicasting; mobility (roaming); open to future change (extension headers); coexistence with existing protocols. _Partial: Two or three correct objectives earn 0.25 (a vague or half-stated set of four also earns 0.25)._
- **P2** (0.5): Objectives are stated specifically enough to be the item asked for (e.g. 'quality of service for real-time traffic', 'simplified header', 'reduce routing table size'), not just generic claims such as 'better' or 'faster'. Four objectives must be given, each with its key term. _Partial: Only some of the objectives are specific, or only two or three are given with their key terms: 0.25._


## saf/IPP_6.2 (1 marks)

**Question:** What are extension headers in IPv6 and where are they located in a packet? What is the main advantage of extension headers compared to IPv4?

**Model answer:** Extension headers are used to extend the fixed IPv6 header with additional, optional network layer information. If present, they are located between the fixed header/main header and payload/upper-layer header/ transport-layer header. Main advantage: One of the following advantages are considered fully correct: 1. It allows the appending of new options without changing the header. 2. IPv6 packets with optional headers are typically processed faster/simpler by intermediate devices as most of the options are ignored (except “Hop-by-Hop Extension”) while they are processed by all routers in IPv4 unless ordered otherwise.

_Marking stance: moderate. Full marks need all three parts: what extension headers are, their location between fixed header and payload, and one valid advantage (either one from the model answer). Part marks go to vague or half-stated parts. A missing or wrong part loses only that part's marks._

- **P1** (0.4): States what extension headers are: optional/additional network-layer information that extends the fixed (main) IPv6 header. _Partial: Half if only vaguely stated (e.g. 'extra headers') without saying optional/extra information extending the fixed IPv6 header._
- **P2** (0.3): States where they are located: between the fixed/main IPv6 header and the payload (upper-layer/transport-layer header), if present. _Partial: Half if only says 'after the main header' or 'before the payload' without both ends._
- **P3** (0.3): Gives one valid main advantage: new options can be added without changing the (fixed) header, OR packets with extension headers are processed faster/simpler by intermediate routers since most options are ignored (except Hop-by-Hop) unlike IPv4 where all routers process options. _Partial: Half if advantage is vague (e.g. 'more flexible' or 'more efficient') without the reason._


## saf/IPP_6.3 (1 marks)

**Question:** What is the “Dynamic Host Configuration Protocol (DHCP)”? What is it used for?

**Model answer:** The Dynamic Host Configuration Protocol (DHCP) is a network management protocol used in Internet Protocol (IP) networks, whereby a DHCP server dynamically assigns an IP address and other network configuration parameters to each device on the network. Further, DHCP has largely replaced RARP (and BOOTP) Uses of DHCP are: Simplifies installation and configuration of end systems. Allows for manual and automatic IP address assignment. May provide additional configuration information (DNS server, netmask, default router, etc.)

_Marking stance: moderate. Full marks need both a definition (server dynamically assigns IP address and config parameters to hosts) and a use (simplifies end-system configuration, automatic/manual address assignment, extra info like DNS, netmask, default router). Give half for a part that is vague or general. Mentioning replacing RARP/BOOTP is not required; give no marks for wrong descriptions such as DHCP translating names or MAC addresses._

- **P1** (0.5): Defines DHCP: a network management protocol in IP networks where a DHCP server dynamically assigns an IP address (and other network configuration parameters) to devices/hosts on the network. _Partial: Half if only vaguely stated (e.g. 'a protocol for IP addresses') without the server dynamically assigning addresses to hosts._
- **P2** (0.5): States what it is used for: automatically/simplifying configuration of end systems by assigning IP addresses (manual or automatic) and providing additional configuration information such as DNS server, netmask, default router. _Partial: Half if only a general purpose is given (e.g. 'configures hosts') without naming IP address assignment or at least one extra parameter such as DNS server, netmask or default router._


## saf/LM_2.1 (1 marks)

**Question:** What is "frame bursting"? Also, give 1 advantage and disadvantage compared to the carrier extension.

**Model answer:** Frame bursting reduces the overhead for transmitting small frames by concatenating a sequence of multiple frames in one single transmission, without ever releasing control of the channel. Advantage :it is more efficient than carrier extension as single frames not filled up with garbage. Disadvantage :need frames waiting for transmission or buffering and delay of frames

_Marking stance: moderate. Full marks need a correct definition, one advantage and one disadvantage relative to carrier extension. Give part marks for vague or half-stated parts; a general statement without the specific advantage or disadvantage earns about half of that point. Wrong statements lose only that point. Marks sum to 1 and may be given in quarter steps overall._

- **P1** (0.34): Defines frame bursting: concatenating/sending multiple frames in one transmission (a burst) without releasing control of the channel, reducing overhead for small frames. _Partial: Half if only says multiple frames sent together, without keeping the channel or reducing overhead for small frames._
- **P2** (0.33): Gives one advantage over carrier extension: more efficient because frames are not padded with extension/garbage bits (less wasted bandwidth). _Partial: Half if says only 'more efficient' or 'less overhead' without linking to no padding._
- **P3** (0.33): Gives one disadvantage versus carrier extension: needs frames queued/buffered waiting to be sent, causing delay of frames. _Partial: Half if mentions complexity or delay vaguely without the need for waiting/buffered frames._


## saf/LM_4.1 (1 marks)

**Question:** What happens to the "collision domain diameter" if you use CSMA / CD and increase the speed of a network by a factor of 10, eg from 10Mb / s to 100Mb / s (all else being equal)?

**Model answer:** Diameter decreases by a factor of 10, e.g 300m to 30m.

_Marking stance: moderate. Full marks need both the direction (decrease) and the size (factor of 10, example 300 m to 30 m is optional). Give part marks if only the decrease is stated or the amount is vague. Give no marks for saying it increases or stays the same._

- **P1** (0.5): States that the collision domain diameter decreases (gets smaller) when the speed is increased. _Partial: Half if only says it is affected/changes or gives the wrong magnitude but correct direction is clear._
- **P2** (0.5): States that it decreases by a factor of 10 (e.g. about 300 m to about 30 m). _Partial: Half if a reduction is given with a vague or approximate amount (e.g. 'much smaller') without the factor of 10._


## saf/MM_8.1 (1 marks)

**Question:** WHAT are the challenges of Mobile Routing compared to routing in fixed and wired networks? Please NAME and DESCRIBE two challenges.

**Model answer:** Possible Challenges: 1.Adaptation: The network has to handle the dynamic positioning of the nodes/topology changes. Additionally, nodes can leave or join the network anywhere (within signal range) at any time. 2.Security: Interception of packets or injection of faulty packages is easily possible in wireless networks. This may necessitate encryption and authentication. 3.Medium Access Control: Wireless networks feature new possibilities for inference and collisions of the transmitted signals. See the following correct example challenges: i)Hidden Terminal: Nodes’ transmissions may collide at other nodes without them noticing, because they are out of detection range of each other (A and C in this example) and therefore sense the medium to be free even though there is an overlap of the transmission ranges. ii)Exposed Terminal: Nodes (C in this example) may not realize they could send collision-free, because a node in their detection range (B) is sending and they, therefore, detect the medium as busy, but the sending node (B) is out of the detection range of the destination node (D) so that no collision would occur. iii)Near and Far Terminals: Signal strength decreases proportionally to the square of distance, so closer nodes may drown out the weaker signals of nodes farther away. 4.Quality of Service (QoS): Due to the rapidly changing network topology, imprecise network information, and resource constraints of participating nodes, it is challenging to provide the desired QoS. Additionally, signal quality may also decline due to noise and occlusion. 5.Scalability: Since it is not possible to know the number of participating nodes beforehand, it is vital that routing protocols, etc. are capable of dealing with increasing network sizes and workloads. 6.Heterogeneity: Nodes may have different capabilities, responsibilities, and constraints, e.g. processing capacity, transmission ranges 7.Dependability: Providing consistent, performant, and reliable routing behavior that higher-level services can trust is challenging in such a dynamic environment. 8.Power Consumption: As most mobile devices are battery-powered, power consumption becomes an important optimization factor in routing, etc.

_Marking stance: moderate. Full marks need two different challenges from the model answer's list, each named and briefly described (e.g. power consumption: battery-powered devices so routing must save energy). A challenge that is only named, or only vaguely described, earns half of that point. Challenges that are wrong or not wireless/mobile-specific earn nothing, and a repeated or merged challenge counts once._

- **P1** (0.5): First challenge: a valid challenge from the model answer is named (e.g. adaptation to topology changes, security, medium access control/hidden-exposed-near-far terminals, QoS, scalability, heterogeneity, dependability, power consumption) AND described correctly in line with the model answer. _Partial: Half marks (0.25) if only named with no or vague description, or described correctly but the name/term is missing or the description has a minor error._
- **P2** (0.5): Second, different challenge: a valid challenge from the model answer is named AND described correctly in line with the model answer. _Partial: Half marks (0.25) if only named with no or vague description, or described correctly but the name/term is missing or the description has a minor error._


## saf/MM_8.2 (1 marks)

**Question:** WHAT is the purpose of Reverse Path Forwarding and Reverse Path Broadcast? HOW do they work?

**Model answer:** Purpose: Both implement a more efficient kind (in terms of duplicate packets) of broadcasting than flooding / to minimize the number of duplicate packets in the network when broadcasting. Reverse Path Forwarding: Each node has a routing table stemming from unicast routing algorithms. When receiving a packet of sender S from neighbor N at node X, check the routing table and only forward the packet to all adjacent nodes (except for N) when you would send packets to S over N → the assumption is that the packet used the BEST route until now. Reverse Path Broadcast: Nodes monitor unicast traffic to learn which paths in the network they are a part of, that is node X knows that is on the best path between two nodes A and B if it receives unicast packets coming from A and going to B or visa versa. In other words, each node knows which spanning trees it is part of in the network. Reverse Path Broadcasting works identical to Reverse Path Forwarding with the exception that it only forwards packets on edges that are part of a spanning tree (again excluding the incoming line to N).

_Marking stance: moderate. Full marks need the purpose (fewer duplicates than flooding), how RPF decides to forward (route back to the source goes via the incoming neighbour), and how RPB differs (only spanning-tree edges, learned from unicast traffic). Give part marks for half-stated or vague mechanisms. A general statement like "they broadcast packets" with no mechanism earns about half at most; wrong mechanisms earn nothing for that point._

- **P1** (0.25): Purpose: both provide broadcasting that is more efficient than flooding, i.e. they reduce/minimise duplicate packets in the network. _Partial: Says only that they are used for broadcasting, without the idea of fewer duplicates/better than flooding._
- **P2** (0.5): Reverse Path Forwarding: using the unicast routing table, a node X receiving a packet from source S via neighbour N forwards it to all other neighbours (not back to N) only if X would send packets to S via N (i.e. the packet arrived on the best path back to S); otherwise it discards it. _Partial: Mentions checking the path/routing table toward the source but omits the condition on N or the forwarding to all other neighbours._
- **P3** (0.25): Reverse Path Broadcast: works like RPF but forwards only on edges that are part of a spanning tree; nodes learn which trees they belong to by monitoring unicast traffic (X is on the best path between A and B if it sees unicast packets between them). _Partial: States it is RPF restricted to spanning-tree edges, or the traffic-monitoring idea, but not both._


## saf/MM_8.3 (1 marks)

**Question:** WHICH PROPERTY of spanning trees makes them appealing for broad- and multicasting? EXPLAIN how you can modify Link State Routing to construct a spanning tree for multicasting.

**Model answer:** Property: There is a single unique path between every pair of nodes in the tree. Alternatively, you can say that spanning trees are subnets of a network that do not contain loops but contain all nodes. This means that no unnecessary duplicates are distributed in the network when forwarding packets using that tree structure. Spanning Tree with Link State Routing: Each intermediate system knows which multicast groups it belongs to, but initially doesn’t know which other IS belong to the groups. Therefore, you can add multicast group information to the link state packet and each node can construct multicast trees once the full network topology and group information are distributed in the whole network, as each node then has the complete state information stored locally (e.g. with Prim or Kruskal)

_Marking stance: moderate. Full marks need the unique-path/loop-free property with its no-duplicates benefit, plus both parts of the modification: group info added to link state packets, and each node then building the tree locally. Part marks for vague or half-stated ideas, such as only saying "no loops" or "send group info" without more. No marks for a wrong property (e.g. shortest paths or lowest cost) or for describing unmodified link state routing only. Naming Prim or Kruskal is not required._

- **P1** (0.4): Names the property: a spanning tree has a single unique path between every pair of nodes (equivalently: it is loop-free yet connects all nodes), so no unnecessary duplicates of packets are sent when broad-/multicasting. _Partial: Half if only says loop-free or connects all nodes without the unique-path/no-duplicates consequence, or states the property vaguely._
- **P2** (0.3): Modification: multicast group membership information is added to the link state packets, so each node learns which nodes/ISs belong to which multicast groups (a node initially knows only its own groups). _Partial: Half if only says link state packets are extended or group info is flooded, without clearly linking it to group membership._
- **P3** (0.3): Once topology and group information are distributed to all nodes, each node locally computes the multicast spanning tree from its complete stored state (e.g. with Prim or Kruskal). _Partial: Half if says nodes compute a tree but not that it is computed locally from the full topology plus group information._


## saf/PE_12.1 (1 marks)

**Question:** Let us assume that you flip a coin 6 times where the probability of heads (H) showing up is 0.6. Please arrange the following events in the increasing order of their likelihood (i.e., least probable → most probable): ● Event A: you see at least three H’s ● Event B: you see the sequence HHHTTT ● Event C: you see exactly three H’s Include justification in your answer headers.

**Model answer:** The correct sequence is BCA , where B is the least probable. One of the following justifications should be given: ● Event B is a subset/part/special case of C, and C is a subset/part/special case of A ● Event B is more specific/strict than C and C is more specific/strict than A ● An actual, correct calculation of the probabilities: ○ P(B) = 0.6 * 0.6 * 0.6 * 0.4 * 0.4 *0.4 = 0.6^3 *0.4^3 = 0.013824 ○ P(C) = (6 choose 3) * P(B) = 0.27648 ○ P(A) = P(C) + P(Y=4) + P(Y=5) + P(Y=6) = 1 - P(Y=0) - P(Y=1) - P(Y=2) = (6 choose 3) * 0.6^3 * 0.4^3 + (6 choose 4) * 0.6^4 * 0.4^2 +(6 choose 5) * 0.6^5 * 0.4 + (6 choose 6) * 0.6^6 = 0.27648 + 15 * 0.020736 + 6 * 0.031104 + 1 * 0.046656 = 0.8208 ○ The answer may be rounded to up to 2 decimal places, e.g. P(B) = 0.01 or P(B) = 0.014 ○ It is also sufficient to give a formula without the actual calculation, if it is apparent that P(B) less than P(C) less than P(A), e.g. by stating P(C) = 20 * P(B)

_Marking stance: moderate. Full marks need the correct order BCA plus a valid justification (subset/specificity argument or correct probabilities/formulas). Give part marks if the order is right but justification is incomplete or has a minor error, or justification is right but order is stated slightly wrongly. A wrong order earns no marks for P1; an answer with no justification cannot earn P2._

- **P1** (0.5): States the correct order: B least probable, then C, then A most probable (B < C < A, i.e. BCA). _Partial: Half if order is mostly right but with a minor slip (e.g. reversed notation), otherwise none._
- **P2** (0.5): Gives a valid justification: B is a subset/special case/more specific than C, and C is a subset/special case of A; OR correct probability calculations/formulas showing P(B)<P(C)<A (e.g. P(B)=0.6^3*0.4^3≈0.014, P(C)=20*P(B)≈0.28, P(A)≈0.82; rounding to 2 d.p. allowed). _Partial: Half if justification covers only one of the two relations (B vs C or C vs A) or has a minor calculation slip; none if justification is missing or vague._


## saf/PE_12.2 (1 marks)

**Question:** Consider a single server queueing system with a buffer of size 10. Let us assume that 9 packets arrive per second and 10 packets are served per second on an average. Assume you monitor the system for exactly one minute after the system reaches equilibrium. How many seconds would you expect the system to be in a state in which there are less than 10 packets waiting in the queue? You need to justify your answer by showing steps involved; calculations, however, need not be included. headers.

**Model answer:** Since we have a buffer size (N) of 10, we will always have less than 10 packets waiting in the queue unless there are exactly 10 packets in the queue. Therefore, we first calculate the probability of the system being full/having 10 packets in the queue. This is also called “blocking probability” or P_B. P_B = ((1 - utilization) * utilization^N) / 1 - utilization^(N+1) = ((1-0.9) * 0.9^10) / (1 - 0.9^11) = 0.0508 Alternatively to the blocking probability, it is also valid to directly calculate P(X less than 10) = (1 -P_B) by summing up the probabilities for 0, 1, …, 9 packets to be in the queue. To calculate the expected time where the system is not blocked in the 60-second observation time-frame, we simply multiply the time frame with P(X less than 10) or the complement of P_B (0.25p) = 60 * (1-P_B) = 56.9512 seconds

_Marking stance: moderate. Full marks need the full-buffer (blocking) reasoning, the M/M/1/N probability with ρ = 0.9, and the final step of multiplying by 60 to get about 56.95 s. Give part marks for a correct method with a numerical slip or a missing value. Give no marks for a bare number with no justification, or for M/M/1 without a finite buffer. Marks are awarded in quarter steps overall, so round the total to the nearest 0.25._

- **P1** (0.33): Recognises that with buffer size N = 10, the system has fewer than 10 packets except when it is full (exactly 10 packets), so the answer needs the blocking/full-state probability P_B (or equivalently P(X<10) = 1 − P_B, or a sum of state probabilities 0..9).
- **P2** (0.34): Calculates the probability using the M/M/1/N formula with utilization ρ = 9/10 = 0.9: P_B = ((1−ρ)ρ^N)/(1−ρ^(N+1)) ≈ 0.0508, so P(X<10) ≈ 0.949. _Partial: Half if the correct formula or approach is stated but the numeric value is wrong or missing._
- **P3** (0.33): Multiplies the 60 s observation time by P(X<10) = 1 − P_B to get the expected time, about 56.95 seconds (≈57 s). _Partial: Half if the multiplication by 60 is shown with a wrong probability._


## saf/PE_12.3 (1 marks)

**Question:** To model the packet arrivals as a poisson process, we assumed that the arrivals for each time interval Δt are independent. Does this assumption hold for real INTERNET traffic? Explain your answer in 2-5 sentences.

**Model answer:** No. Real internet traffic often comes in bursts. Therefore, arrivals are not independent because the probability of an arrival happening at a node is influenced by previous arrivals at the node. For example, on-demand video streams selectively load the next video segments when needed. This means the actual network utilization depends on the current playback state on the client-side. The packet arrivals are not independent, as it is likely that there is a low utilization directly after the next segments have been loaded.

_Marking stance: moderate. Full marks: says independence does not hold, mentions bursty traffic, and explains that arrivals depend on previous arrivals, ideally with an example like video segment loading. Part marks: a bare \"no\" or a vague reason (e.g. \"traffic is bursty\" with no link to dependence). No marks for answering \"yes\" or for reasons unrelated to dependence between arrivals._

- **P1** (0.5): States that the independence assumption does not hold for real internet traffic (answer is "No"), noting that traffic is bursty. _Partial: Half if only says "no" without mentioning burstiness or dependence, or mentions bursts but the conclusion is unclear._
- **P2** (0.5): Explains why: arrivals depend on previous arrivals (the probability of an arrival is influenced by earlier arrivals), supported by an example such as on-demand video streaming loading segments, giving low utilization right after a segment is loaded. _Partial: Half if dependence on earlier arrivals is stated vaguely or the example is given without linking it to dependence between intervals._


## saf/SDN_11.1 (1 marks)

**Question:** Software-defined Networking (SDN) introduces separate control and data planes to manage network flows. Please explain the responsibilities of each plane in 1-2 sentences. Further, name two tasks the SDN controller takes care of.

**Model answer:** Control Plane: The control plane is logically centralized, but can be physically distributed (multiple coordinating control servers for higher availability and scalability). One of the following responsibilities should be given: ● decides the route for the packet/data ○ Control servers manage the network graph, define routes, and update the flow tables of connected switches. ● handles unprocessed packets coming in from the data plane Data plane: Responsible for packet forwarding. Individual switches just execute actions according to their flow tables decided upon by the control plane. The following are the tasks taken care of by the controller: ● Configuration of forwarding tables ● Injecting packets ● Events from switch (packet-in) ● Collection/Monitoring of traffic statistics ● Discovery of topology ● Inventorying what devices are within the network and the capabilities of each device ● Interfaces with control logic (control “application”) via the northbound interface(s) ● Implements a southbound interface to interact with the data plane. ● Implements the control plane.

_Marking stance: moderate. Full marks need the control plane role, the data plane role, and two valid controller tasks. Give part marks for a vague role description or only one valid task. Give no marks for a part that is wrong or reversed (e.g. data plane deciding routes). The tasks must be specific items, not just 'manages the network'._

- **P1** (0.4): Control plane responsibility: decides/computes routes (manages network graph, sets flow tables of switches) and/or handles packets the data plane cannot process; logically centralized. _Partial: Half if only vaguely stated (e.g. 'controls the network') without routing/flow-table decisions._
- **P2** (0.3): Data plane responsibility: forwards packets; switches simply execute actions according to flow tables set by the control plane. _Partial: Half if only says 'handles traffic' without forwarding per flow tables._
- **P3** (0.3): Names two tasks of the SDN controller from the model list (e.g. configuring forwarding tables, injecting packets, handling packet-in events, traffic statistics monitoring, topology discovery, device inventory, northbound/southbound interfaces, implementing the control plane). _Partial: Half (0.15) if only one valid task is named._


## saf/SDN_11.2 (1 marks)

**Question:** What are the benefits and drawbacks of SDN compared to traditional networking,where each switch/router has to manage forwarding and routing on its own? Describe two benefits and two drawbacks in 1-2 sentences each.

**Model answer:** Benefits: ● Reduced complexity of the switches: They only have to act according to their flow tables and do not have to make any local routing decisions. ● Due to centralized routing, the routing can converge way faster to a global optimum than with decentralized routing because of a global view ● Better Integration of application and network provides a better global view of the system. ● Increased flexibility : 1. We can update the routing logic on the fly, routers/switches are not limited to hard-coded routing algorithms anymore (Note: this is also possible with programmable switches). 2. API to “program” the network: Software (application) “defines” the network 3. High-level programming languages for implementation of logic and making use of powerful integrated development environments. Note: In case the reasoning/example sufficiently explains the benefit, naming like reduced complexity, increased flexibility can be omitted and response can still be granted 0.25 for each benefit. Drawbacks: ● High complexity of the control servers: They have to make all the routing decisions for the (sub)network and can therefore be a bottleneck. ● Centralized routing in distributed systems in general: The routing completely depends on the control server(s). To achieve better availability and fault tolerance, the number of control servers can be increased. However, this can lead to synchronization and consistency issues. → CAP problem (consistency, availability, partition tolerance) ● New technology adoption challenges: ● Switching to SDN from traditional networking. ● Training personnel on SDN. All these will cost depending on the reconfiguration level but then for the long term, it depends upon the ROI. ● Security-related concerns : ○ Lack of hardware security: eliminating the use of the physical routers and switches, one also loses the security that comes with it.

_Marking stance: moderate. Full marks need two valid benefits and two valid drawbacks, each with a short reason. Each benefit or drawback is worth 0.25. A bare label with no reason, or a half-correct one, earns half of that. A wrong or off-topic item earns nothing, and it does not affect the other items. Do not credit the same idea twice._

- **P1** (0.5): Gives two benefits of SDN over traditional networking, each with a brief explanation. Acceptable benefits: simpler switches (they only follow flow tables, no local routing decisions); faster convergence to a global optimum through centralized routing with a global view; better integration of applications and network; more flexibility (routing logic updated on the fly, programmable via API or high-level languages). Each benefit is worth 0.25. _Partial: 0.25 for each correct benefit. Give half of that (0.125) if the benefit is only named or vaguely stated, such as 'more flexible' with no reason._
- **P2** (0.5): Gives two drawbacks of SDN, each with a brief explanation. Acceptable drawbacks: the control server is complex and can become a bottleneck; dependence on centralized control, where adding servers for availability causes synchronization and consistency problems (CAP); the cost and effort of adopting SDN and training staff; security concerns such as the loss of hardware security. Each drawback is worth 0.25. _Partial: 0.25 for each correct drawback. Give half of that (0.125) if the drawback is only named or vaguely stated, such as 'security issues' with no reason._


## saf/SDN_11.3 (1 marks)

**Question:** Name the two modes of control plane distribution and name one downside for each of them.

**Model answer:** Two modes of physical distribution of control plane and associated drawbacks are: Replication ● Issue of scalability ● More resources, more cost ● Wastage of resources as the replicated node is on standby and no actual load distribution occurs. ● The problem to keep the data consistent in the replicated node is hard and complex. Partitioning ● Raises issues similar to P2P networks ● Knowledge about neighborhood ● Coordination and consistency ● Lower availability

_Marking stance: moderate. Full marks need both modes named (replication, partitioning) and one correct downside for each. Give part marks when only one mode or one downside is correct, or when a downside is vague. A downside is only credited if it fits the mode it is attached to; give no marks for wrong modes or generic statements._

- **P1** (0.5): Names the two modes of control plane distribution: replication and partitioning (both must be named). _Partial: Half marks if only one mode is named correctly._
- **P2** (0.5): Gives one valid downside for each mode: for replication, e.g. scalability issue, extra resources/cost, standby wastage with no load distribution, or hard data consistency; for partitioning, e.g. P2P-like issues, neighbourhood knowledge, coordination/consistency, or lower availability. _Partial: Half marks if a valid downside is given for only one mode, or if downsides are vague._


## saf/SDN_11.4 (1 marks)

**Question:** In an SDN, switches maintain a pipeline of flow tables and a meter table. Summarize their respective functions in one sentence each.

**Model answer:** Meter table: collects flow statistics or contains meter entry per flow (0.25) which is taken into account by the controller for management of the network like QoS operation(rate-limiting being one of them). Flow pipeline: consists of flow tables that contain “rules” or fields (0.25) for packet forwarding(0.25) /actions to be taken on the packets or in other words it implements the routing logic in the switch

_Marking stance: moderate. Full marks need both functions: meter table (per-flow meter entries/statistics for QoS such as rate-limiting) and flow pipeline (flow tables with rules/actions for forwarding). Give half of a part if it is vague or only partly correct. Give no marks for a part that is missing, swapped between the two tables, or wrong._

- **P1** (0.5): Meter table function: holds a meter entry per flow / collects flow statistics, used by the controller for network management such as QoS (e.g. rate-limiting). _Partial: Half if only vaguely stated (e.g. 'measures/monitors traffic') without mentioning per-flow meters/statistics or QoS/rate-limiting._
- **P2** (0.5): Flow pipeline function: a series of flow tables containing rules (match fields) and actions, used for packet forwarding / deciding what actions are applied to packets (the switch's routing logic). _Partial: Half if only says flow tables 'store rules' or 'handle packets' without linking to forwarding/actions._


## saf/TC_10.1 (1 marks)

**Question:** State at least 4 of the differences shown in the lecture between the UDP and TCP headers.

**Model answer:** Possible Differences : The UPD header (8 bytes) is much shorter than the TCP header (20-60 bytes) The UDP header has a fixed length while the TCP header has a variable length Fields contained in the TCP header and not the UDP header : -Sequence number -Acknowledgment number -Reserved -Flags/Control bits -Advertised window -Urgent Pointer -Options + Padding if the options are UDP includes the packet length (data + header) while TCP has the header length/data offset (just header) field instead The sender port field is optional in UDP, while the source port in TCP is necessary to establish the connection

_Marking stance: moderate. Full marks need four distinct, correct differences between UDP and TCP headers, each worth a quarter. Separately listed TCP-only fields (e.g. sequence number and flags) may each count as one difference. Vague or wrong statements earn nothing for that difference, and fewer than four correct differences gives proportionally fewer quarters._

- **P1** (0.25): States at least one correct difference in header size or length: UDP header is short/fixed (8 bytes) while TCP header is longer/variable (20-60 bytes). _Partial: Half if only says one is shorter/longer without fixed vs variable or sizes, and this is the only length statement._
- **P2** (0.25): States a correct difference in fields: TCP has fields UDP lacks (e.g. sequence number, acknowledgment number, flags/control bits, advertised window, urgent pointer, options+padding, reserved). _Partial: Half if only vaguely says TCP has more fields without naming any._
- **P3** (0.25): States a correct difference in length fields: UDP has a packet length (header + data) field, while TCP has header length/data offset (header only). _Partial: Half if mentions only one of the two fields or does not say what it covers._
- **P4** (0.25): States a correct difference in source port: optional in UDP, but necessary in TCP to establish the connection. A further distinct correct TCP-only field may be accepted to reach four differences. _Partial: Half if only says source port differs without saying optional vs required._


## saf/TC_10.2 (1 marks)

**Question:** In the lecture you have learned about congestion control with TCP. Name the 2 phases of congestion control and explain how the Congestion Window (cwnd) and the Slow Start Threshold (ss_thresh) change in each phase (after initialization, where cwnd = 1 and ss_thresh = advertised window size) in 1-4 sentences .

**Model answer:** Slow start (cwnd less than ss_thresh): In the slow start phase, cwnd is incremented by one every time a segment is acknowledged. This results in an exponential growth as cwnd is essentially doubled after each Round Trip Time (RTT). This is done until either a packet is lost or ss_thresh is reached. When cwnd >= ss_thresh, the congestion avoidance phase is entered. After a packet is lost / congestion the following adaption is made in both phases: ss_thresh = cwnd / 2. Then cwnd is reset to 1. Congestion Avoidance (cwnd >= ss_thresh):: In the congestion avoidance phase, cwnd is incremented more slowly. There are different incrementation strategies, but they usually grow linearly, e.g. only increment cwnd by 1 after all sent segments have been acknowledged. This is done until a packet is lost. Typically, this means that cwnd less than ss_thresh and the slow start phase is entered again. After a packet is lost / congestion the following adaption is made in both phases: ss_thresh = cwnd / 2. Then cwnd is reset to 1.

_Marking stance: moderate. Full marks need both phases named plus how cwnd changes in each (exponential in slow start, linear in congestion avoidance). Give part marks for vague growth descriptions without exponential/linear or for naming only one phase. Mentioning that on loss ss_thresh = cwnd/2 and cwnd resets to 1 is correct extra detail but not required; a wrong statement loses only that point._

- **P1** (0.25): Names the two phases: slow start and congestion avoidance. _Partial: Only one phase named correctly._
- **P2** (0.375): Slow start: cwnd grows exponentially (increased by 1 per ACK, i.e. doubling each RTT) while cwnd < ss_thresh; ss_thresh is not changed during normal growth. _Partial: Says cwnd grows fast/increases but not exponential or per-ACK/RTT detail._
- **P3** (0.375): Congestion avoidance (cwnd >= ss_thresh): cwnd grows slowly/linearly (e.g. +1 per RTT / after all segments are acknowledged). _Partial: Says cwnd grows slower but gives no linear rule._


## saf/TC_10.3 (1 marks)

**Question:** Transparent bridges manage a bridge table for the forwarding process. Please describe what information the table holds and how it is modified during the backwards learning phase. How is the table used in the forwarding process and what is one benefit of that? Please answer the question in 2-5 sentences.

**Model answer:** 1.A mapping between destinations/stations (MACs) and outgoing LAN interfaces. 2.This table is initially empty and received packages are flooded on every line. When a bridge receives a frame (as the bridge runs in promiscuous mode it listens in on all the traffic arriving at its LAN links) with source address Q on LAN L, it adds the timestamped entry “Q can be reached over L” to the table and the next time a packet with destination Q arrives, it is forwarded on link L. The time-stamp is used to update or purge old entries. Therefore, it learns by observing the incoming traffic. 3.To do selective forwarding instead of flooding. 4.i)less duplication/unnecessary flooding is prevented. ii)less congestion. iii)better bandwidth usage than flooding.

_Marking stance: moderate. Each of the four parts asked for (table contents, learning update, use in forwarding, one benefit) is worth a quarter mark. Accept different wording, but the mapping of MAC/station to LAN/port and learning from the source address of incoming frames must be present. Vague or half-stated parts earn half of that quarter; a wrong statement loses only that part._

- **P1** (0.25): States what the table holds: a mapping of destination stations/MAC addresses to the outgoing LAN interface/port (which LAN each station can be reached over). _Partial: Half if only says it holds addresses or ports without the mapping between them._
- **P2** (0.25): Describes how the table is modified in backward learning: starts empty; on receiving a frame with source address Q on LAN L, the bridge adds/updates the entry 'Q reachable via L' (timestamped, old entries purged), i.e. learns from observed incoming traffic. _Partial: Half if it says the table is filled from incoming traffic but omits the use of the source address and arrival LAN._
- **P3** (0.25): Describes use in forwarding: the bridge looks up the frame's destination address and forwards it only on the associated link (flooding if unknown). _Partial: Half if it says the table is looked up for forwarding without destination-to-link detail._
- **P4** (0.25): Gives one benefit: selective forwarding instead of flooding, reducing unnecessary traffic/duplication/congestion or improving bandwidth use. _Partial: Half if benefit is vague (e.g. 'more efficient') without reference to reduced flooding or traffic._
