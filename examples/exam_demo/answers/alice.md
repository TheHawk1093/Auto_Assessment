Q1. TCP gives every byte a sequence number and the receiver acknowledges what it has received. If an acknowledgement does not arrive before the timer runs out the sender sends the segment again. There is also a checksum so corrupted segments are dropped, and a receive window tells the sender how much it may send.

Q2a. Bandwidth-delay product is the link rate times the one-way delay, which is how many bits can be on the wire at once.

Q2b. 10 Mbps is 10,000,000 bits per second and 20 ms is 0.02 s, so 10,000,000 x 0.02 = 200,000 bits.

Q3. Because more than one prefix in the table can match, and the longest is the most specific route, so the packet goes along the best-matching path. This allows route aggregation with exceptions.
