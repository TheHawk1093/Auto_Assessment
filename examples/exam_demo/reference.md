# Marking guide

## Question 1 (4 marks)
Model answer: TCP numbers every byte with sequence numbers, the receiver sends cumulative acknowledgements, and the sender retransmits a segment when its timer expires or after three duplicate ACKs. A checksum detects corrupted segments, and flow control with a receive window stops the sender from overrunning the receiver.
Rubric: 1 mark sequence numbers and acknowledgements; 1 mark retransmission on timeout or duplicate ACKs; 1 mark checksum for error detection; 1 mark flow control by the receive window. Half marks allowed where an idea is only named.

## Question 2
2(a) Model answer: the bandwidth-delay product is the capacity of the link multiplied by its one-way propagation delay; it is the amount of data that can be in flight on the link. (2 marks: 1 for the formula, 1 for the meaning.)
2(b) Model answer: 10 Mbps x 20 ms = 10,000,000 x 0.02 = 200,000 bits. Rubric: 1 mark for converting units correctly, 1 mark for multiplying capacity by delay, 1 mark for the correct answer 200,000 bits.

## Question 3
Model answer: Several routing table entries can match one destination address, for example 10.0.0.0/8 and 10.1.0.0/16. The longest matching prefix is the most specific route, so the router picks it; this lets networks aggregate routes while still allowing exceptions.
