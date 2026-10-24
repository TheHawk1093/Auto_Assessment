# saf: sized rubrics

Marks per point add up to the question total.

## saf/DLL_2.2 (1 marks)

**Question:** What is the difference between asynchronous and synchronous transmission mode in the Data Link Layer.

**Model answer:** Asynchronous transmission: Every character a self-contained unit surrounded by a start bit and a stop bit, which is an easy and cheap pattern, but causes low transmission rates. Synchronous transmission: Several characters pooled to a continuous stream of data (frames), Frames defined by SYN or flag, higher complexity, but higher transmission rates. Requires synchronization between sender and receiver.

- **P1** (1): Correctly contrasts the two modes: asynchronous sends each character as an independent unit framed by a start bit and a stop bit (simple/cheap, low transmission rate), whereas synchronous sends many characters pooled together as a continuous stream/frame delimited by SYN/flag, needing sender-receiver synchronization (more complex, higher transmission rate). Equivalent wording accepted. _Partial: Award half if only one mode is described correctly, or the modes are described without the contrast (e.g., start/stop bits per character vs. blocks/frames)._


## saf/DLL_2.3 (1 marks)

**Question:** What requirement has to be met so that you can use the piggybacking extension to the sliding window protocol?

**Model answer:** Piggybacking only makes sense if there is a full-duplex or semi-duplex connection between sender and receiver i.e. two-way communication or Frames must contain additional field for acknowledgement.

- **P1** (1): States that piggybacking requires a two-way (full-duplex or half/semi-duplex) connection between sender and receiver, with data frames flowing in both directions so that acknowledgements can be carried in the data frames (frames having an extra acknowledgement field). Equivalent wording accepted.


## saf/IPP_6.1 (1 marks)

**Question:** What are the objectives of IPv6? Please state at least 4 objectives.

**Model answer:** To support billions of end-systems. To reduce routing tables. To simplify protocol processing with Simplified header. To increase security. To support real time data traffic (quality of service). Flow label, traffic class. To provide multicasting. To support mobility (roaming). To be open for change (future): extension headers for additional change incorporation. To coexistence with existing protocols.

- **P1** (1): States at least 4 valid objectives of IPv6 from the following (equivalent wording accepted): support billions of end-systems (large address space); reduce routing table size; simplified header / simpler protocol processing; increased security; support real-time traffic / quality of service (flow label, traffic class); multicasting; mobility (roaming); openness to future change (extension headers); coexistence with existing protocols. _Partial: Half credit (0.5) if exactly 2 or 3 valid objectives are stated._


## saf/IPP_6.3 (1 marks)

**Question:** What is the “Dynamic Host Configuration Protocol (DHCP)”? What is it used for?

**Model answer:** The Dynamic Host Configuration Protocol (DHCP) is a network management protocol used in Internet Protocol (IP) networks, whereby a DHCP server dynamically assigns an IP address and other network configuration parameters to each device on the network. Further, DHCP has largely replaced RARP (and BOOTP) Uses of DHCP are: Simplifies installation and configuration of end systems. Allows for manual and automatic IP address assignment. May provide additional configuration information (DNS server, netmask, default router, etc.)

- **P1** (1): States that DHCP is a network management protocol in which a server dynamically assigns IP addresses (and other network configuration parameters such as DNS server, netmask, default router) to devices on the network, which simplifies configuration of end systems. Equivalent wording accepted.


## saf/LM_4.1 (1 marks)

**Question:** What happens to the "collision domain diameter" if you use CSMA / CD and increase the speed of a network by a factor of 10, eg from 10Mb / s to 100Mb / s (all else being equal)?

**Model answer:** Diameter decreases by a factor of 10, e.g 300m to 30m.

- **P1** (1): States that the collision domain diameter decreases by a factor of 10 (e.g. 300m to 30m). Equivalent wording such as 'becomes ten times smaller' earns the mark. Saying only 'decreases' without the factor of 10 does not.


## saf/MM_8.1 (1 marks)

**Question:** WHAT are the challenges of Mobile Routing compared to routing in fixed and wired networks? Please NAME and DESCRIBE two challenges.

**Model answer:** Possible Challenges: 1.Adaptation: The network has to handle the dynamic positioning of the nodes/topology changes. Additionally, nodes can leave or join the network anywhere (within signal range) at any time. 2.Security: Interception of packets or injection of faulty packages is easily possible in wireless networks. This may necessitate encryption and authentication. 3.Medium Access Control: Wireless networks feature new possibilities for inference and collisions of the transmitted signals. See the following correct example challenges: i)Hidden Terminal: Nodes’ transmissions may collide at other nodes without them noticing, because they are out of detection range of each other (A and C in this example) and therefore sense the medium to be free even though there is an overlap of the transmission ranges. ii)Exposed Terminal: Nodes (C in this example) may not realize they could send collision-free, because a node in their detection range (B) is sending and they, therefore, detect the medium as busy, but the sending node (B) is out of the detection range of the destination node (D) so that no collision would occur. iii)Near and Far Terminals: Signal strength decreases proportionally to the square of distance, so closer nodes may drown out the weaker signals of nodes farther away. 4.Quality of Service (QoS): Due to the rapidly changing network topology, imprecise network information, and resource constraints of participating nodes, it is challenging to provide the desired QoS. Additionally, signal quality may also decline due to noise and occlusion. 5.Scalability: Since it is not possible to know the number of participating nodes beforehand, it is vital that routing protocols, etc. are capable of dealing with increasing network sizes and workloads. 6.Heterogeneity: Nodes may have different capabilities, responsibilities, and constraints, e.g. processing capacity, transmission ranges 7.Dependability: Providing consistent, performant, and reliable routing behavior that higher-level services can trust is challenging in such a dynamic environment. 8.Power Consumption: As most mobile devices are battery-powered, power consumption becomes an important optimization factor in routing, etc.

- **P1** (1): Names and describes two valid challenges of mobile/wireless routing compared to fixed wired networks (e.g. adaptation to topology changes/node mobility, security, medium access control such as hidden/exposed/near-far terminals, QoS, scalability, heterogeneity, dependability, power consumption). Each challenge must be named and given a correct brief description; equivalent wording accepted. _Partial: Half credit (0.5) if only one valid challenge is named and described, or if two valid challenges are named but only one (or neither) is described adequately._


## saf/MM_8.2 (1 marks)

**Question:** WHAT is the purpose of Reverse Path Forwarding and Reverse Path Broadcast? HOW do they work?

**Model answer:** Purpose: Both implement a more efficient kind (in terms of duplicate packets) of broadcasting than flooding / to minimize the number of duplicate packets in the network when broadcasting. Reverse Path Forwarding: Each node has a routing table stemming from unicast routing algorithms. When receiving a packet of sender S from neighbor N at node X, check the routing table and only forward the packet to all adjacent nodes (except for N) when you would send packets to S over N → the assumption is that the packet used the BEST route until now. Reverse Path Broadcast: Nodes monitor unicast traffic to learn which paths in the network they are a part of, that is node X knows that is on the best path between two nodes A and B if it receives unicast packets coming from A and going to B or visa versa. In other words, each node knows which spanning trees it is part of in the network. Reverse Path Broadcasting works identical to Reverse Path Forwarding with the exception that it only forwards packets on edges that are part of a spanning tree (again excluding the incoming line to N).

- **P1** (1): States the purpose: both are broadcast methods that reduce duplicate packets compared with flooding. Explains RPF: a node X receiving a packet from sender S via neighbor N checks its unicast routing table and forwards it to all adjacent nodes except N only if it would send packets to S via N (i.e. packet arrived on the best route). Explains RPB: same as RPF, but nodes learn from unicast traffic which spanning trees/best paths they belong to, and forward only on edges that are part of a spanning tree (excluding the incoming link). Equivalent wording accepted. _Partial: Award 0.5 if the purpose and RPF mechanism are correct but RPB is missing or wrong (or vice versa for a correct RPB with RPF missing)._


## saf/MM_8.3 (1 marks)

**Question:** WHICH PROPERTY of spanning trees makes them appealing for broad- and multicasting? EXPLAIN how you can modify Link State Routing to construct a spanning tree for multicasting.

**Model answer:** Property: There is a single unique path between every pair of nodes in the tree. Alternatively, you can say that spanning trees are subnets of a network that do not contain loops but contain all nodes. This means that no unnecessary duplicates are distributed in the network when forwarding packets using that tree structure. Spanning Tree with Link State Routing: Each intermediate system knows which multicast groups it belongs to, but initially doesn’t know which other IS belong to the groups. Therefore, you can add multicast group information to the link state packet and each node can construct multicast trees once the full network topology and group information are distributed in the whole network, as each node then has the complete state information stored locally (e.g. with Prim or Kruskal)

- **P1** (0.5): States the property: a spanning tree has a single unique path between every pair of nodes (equivalently, it is loop-free yet spans all nodes, so no duplicate packets are forwarded).
- **P2** (0.5): Explains the link state modification: add multicast group membership information to the link state packets, so that once topology and group info are flooded, each node can locally compute the multicast spanning tree (e.g. with Prim or Kruskal). Equivalent wording accepted.


## saf/PE_12.3 (1 marks)

**Question:** To model the packet arrivals as a poisson process, we assumed that the arrivals for each time interval Δt are independent. Does this assumption hold for real INTERNET traffic? Explain your answer in 2-5 sentences.

**Model answer:** No. Real internet traffic often comes in bursts. Therefore, arrivals are not independent because the probability of an arrival happening at a node is influenced by previous arrivals at the node. For example, on-demand video streams selectively load the next video segments when needed. This means the actual network utilization depends on the current playback state on the client-side. The packet arrivals are not independent, as it is likely that there is a low utilization directly after the next segments have been loaded.

- **P1** (1): States that the independence assumption does not hold for real internet traffic, and justifies it: traffic is bursty / arrivals depend on previous arrivals (e.g., video streaming loads segments in bursts, so utilization is low right after a load). Equivalent correct reasoning about dependence between arrivals earns the mark.


## saf/SDN_11.4 (1 marks)

**Question:** In an SDN, switches maintain a pipeline of flow tables and a meter table. Summarize their respective functions in one sentence each.

**Model answer:** Meter table: collects flow statistics or contains meter entry per flow (0.25) which is taken into account by the controller for management of the network like QoS operation(rate-limiting being one of them). Flow pipeline: consists of flow tables that contain “rules” or fields (0.25) for packet forwarding(0.25) /actions to be taken on the packets or in other words it implements the routing logic in the switch

- **P1** (0.5): Meter table: holds a meter entry per flow / collects flow statistics, used for network management such as QoS (e.g. rate-limiting). Equivalent wording accepted.
- **P2** (0.5): Flow pipeline: made up of flow tables containing rules (match fields/actions) that determine packet forwarding / actions on packets, i.e. implements the switch's routing/forwarding logic. Equivalent wording accepted.


## saf/TC_10.3 (1 marks)

**Question:** Transparent bridges manage a bridge table for the forwarding process. Please describe what information the table holds and how it is modified during the backwards learning phase. How is the table used in the forwarding process and what is one benefit of that? Please answer the question in 2-5 sentences.

**Model answer:** 1.A mapping between destinations/stations (MACs) and outgoing LAN interfaces. 2.This table is initially empty and received packages are flooded on every line. When a bridge receives a frame (as the bridge runs in promiscuous mode it listens in on all the traffic arriving at its LAN links) with source address Q on LAN L, it adds the timestamped entry “Q can be reached over L” to the table and the next time a packet with destination Q arrives, it is forwarded on link L. The time-stamp is used to update or purge old entries. Therefore, it learns by observing the incoming traffic. 3.To do selective forwarding instead of flooding. 4.i)less duplication/unnecessary flooding is prevented. ii)less congestion. iii)better bandwidth usage than flooding.

- **P1** (0.25): States the table holds a mapping between stations/destination MAC addresses and the outgoing LAN interface/port (which link each station can be reached over).
- **P2** (0.35): Backward learning: table starts empty; for each received frame the bridge reads the source address Q and the arrival LAN L and adds/updates an entry 'Q reachable via L' (timestamp for refreshing/purging old entries is optional detail). Equivalent wording accepted.
- **P3** (0.25): Forwarding use: the bridge looks up the destination address and forwards the frame only on the associated link (selective forwarding), flooding only when the destination is unknown.
- **P4** (0.15): Names one benefit of this, e.g. less unnecessary flooding/duplication, less congestion, or better bandwidth use.
