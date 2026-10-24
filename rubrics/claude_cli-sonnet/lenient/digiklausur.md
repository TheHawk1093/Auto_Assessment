# digiklausur: lenient rubrics

Marks per point add up to the question total.

## digiklausur/1 (2 marks)

**Question:** Give a definition for the term "artificial neural network" and mention, how it resembles the human brain!

**Model answer:** A neural network is a massively parallel distributed processor which is made up of simple processing units. It has a natural propensity for storing experiential knowledge. Neural networks resemble the brain in two aspects; knowledge is acquired by the network from its environment through a learning process, interneuron connection strength known as synaptic weights are used to store the acquired knowledge.

_Marking stance: lenient. Full marks: a recognisable definition (simple connected units processing in parallel, storing knowledge from experience) plus the brain resemblance (learning from environment; weights/connection strengths store knowledge), in any wording. Part marks: vague or incomplete definition, or only one of the two resemblances. Zero: off-topic or wrong answers; extra incorrect remarks do not cost marks unless they contradict the core idea._

- **P1** (1): Defines an artificial neural network as a network/processor made of many simple processing units (neurons) working in parallel/distributed fashion that stores knowledge from experience and makes it available for use. _Partial: Half if vague, e.g. just 'a system of connected units/neurons' with no mention of simple units, parallel processing or storing knowledge._
- **P2** (1): States how it resembles the brain: knowledge is acquired from the environment through learning, and connection strengths between neurons (synaptic weights) store the knowledge. _Partial: Half if only one of the two resemblances is given, or if the resemblance is stated only vaguely (e.g. 'it has neurons like the brain')._


## digiklausur/10 (2 marks)

**Question:** Explain back propagation, use the correct technical terms!

**Model answer:** Backpropagation lowers the error of a MLP level by level recursively backwards. It back propagates an error from the last layer to the first layer by updating the weights. The updates are determined by the local gradient at each level which is computed by partial derivatives of the error and chain rule.

_Marking stance: lenient. Full marks for saying, in any wording, that the error is passed backwards from output to input layer, adjusting weights, using gradients/derivatives via the chain rule. Give part marks for a vague but related answer, e.g. only 'it updates weights to reduce error' or only 'uses derivatives'. Give 0 for wrong or off-topic answers, such as describing only the forward pass. Extra incorrect remarks do not cost marks unless they contradict the core idea._

- **P1** (1): States that backpropagation reduces the error of a (multi-layer) network by propagating the error backwards from the output/last layer to the first layer, layer by layer, and updating the weights accordingly. _Partial: Half if it only says it reduces error or updates weights, without the backward direction/layer-by-layer idea._
- **P2** (1): States that the weight updates are based on gradients (local gradient / partial derivatives of the error) computed using the chain rule. _Partial: Half if it mentions gradients or derivatives (or gradient descent) but not the chain rule or per-layer computation._


## digiklausur/11 (2 marks)

**Question:** When learning using steepest descent, explain the role of the learning rate? What is a danger?

**Model answer:** Learning rate controls the speed of the convergence. When the learning rate is low, the convergence is overdamped and slow. When the learning rate is high, the convergence is underdamped and follows a zigzagging path. When the learning rate exceeds a critical value learning becomes unstable.

_Marking stance: lenient. Full marks: says the learning rate sets the step size/speed of convergence, and that too large a rate causes instability/divergence (or overshooting). Part marks: vague answers, e.g. only slow vs fast, or only zigzagging without instability. No marks for unrelated or wrong claims. Technical terms like overdamped/underdamped are not required._

- **P1** (1): Role of the learning rate: it controls the step size/speed of convergence (small rate gives slow convergence; larger rate gives faster convergence, possibly oscillating/zigzagging). _Partial: Half if only vaguely says it affects learning/convergence without mentioning speed or step size._
- **P2** (1): Danger: if the learning rate is too high (exceeds a critical value), learning becomes unstable/diverges (oscillation or zigzagging may be mentioned). _Partial: Half if only mentions zigzagging/oscillation or overshooting without instability or divergence, or only says too-small rate is slow._


## digiklausur/12 (2 marks)

**Question:** How does a Reduced Boltzman Machine work (main idea)?

**Model answer:** The reduced Boltzmann machine is a bi-parted graph which works by flipping the states of binary neurons based on a probability determined by the activation produced at the neuron. Neurons are arranged in a visible and a hidden layer in a recurrent fashion. There are two states involved called the clamped state in which the visible neuron is connected to the input and a free running state in which both layers run free.

_Marking stance: lenient. Full marks for conveying the core idea in any wording: a two-layer visible/hidden network of binary units whose states change probabilistically based on activation. Give part marks for a vague or incomplete but related answer (e.g. only the structure or only the probabilistic behaviour). Clamped/free-running phases are a bonus route to P2 but not required; give no marks for unrelated or wrong descriptions._

- **P1** (1): States the basic structure: a two-layer (bipartite) network with a visible layer and a hidden layer of binary neurons. _Partial: Half if only mentions visible/hidden or binary neurons vaguely._
- **P2** (1): States the working principle: neuron states are flipped/set stochastically with a probability determined by the neuron's activation, and/or the learning uses a clamped phase (visible tied to input) and a free-running phase. _Partial: Half if only says it is probabilistic or has two phases, without detail._


## digiklausur/13 (2 marks)

**Question:** Define: Echo State Network (ESN), how are they different to FF NNs?

**Model answer:** Echo State Network is a type of Recurrent Neural Network and has at least one cyclic (feedback) connection. Only the weights of the output layers are updated while learning. ESN consists of feedback connections while a FF NN does not. ESN can approximate dynamic systems while FF NN cannot.

_Marking stance: lenient. Full marks: says an ESN is a recurrent network with feedback connections, and that unlike FF NNs (no feedback) it can handle dynamic systems. Give part marks for vague but related answers, e.g. mentions memory, time series or only training the output weights without the feedback idea. Give no marks for wrong or unrelated answers. Technical terms are not required and extra remarks do not cost marks._

- **P1** (1): Defines ESN as a type of recurrent neural network, i.e. it has feedback/cyclic connections (and/or only the output-layer weights are trained). _Partial: Half if vague, e.g. says it is a type of neural network with memory or loops but not clearly recurrent/feedback._
- **P2** (1): Says how it differs from FF NNs: ESN has feedback (cyclic) connections while FF NNs do not (so ESN can handle/approximate dynamic systems, FF NNs cannot). _Partial: Half if the difference is vague, e.g. ESN handles time/sequences better, without mentioning feedback connections._


## digiklausur/14 (2 marks)

**Question:** Describe: the structure on an CNN.

**Model answer:** Convolutional Neural Network consists of many layers such as a convolutional layer that has kernels which convolve over the input image, an activation layer (ReLU activation), pooling layer (max or average pooling), and one or more fully connected layers followed by softmax layer.

_Marking stance: lenient. Full marks for listing the main layers in a CNN in any wording: convolution and pooling, then fully connected and output layers, with activation mentioned. Give part marks if the answer names some layers but leaves out a main group. Give no marks if the answer is off-topic or describes a different network. Missing details such as the exact pooling type or softmax cost nothing._

- **P1** (1): Names the main building blocks of a CNN: convolutional layer(s) (kernels/filters sliding over the input image) together with pooling layer(s) (max or average), in any wording. _Partial: Half if only one of convolution or pooling is given, or the description is vague._
- **P2** (1): States that after the convolution/pooling stages there are fully connected layer(s) leading to an output (softmax) layer, with an activation such as ReLU in the structure. _Partial: Half if only fully connected/output layer or only activation is mentioned._


## digiklausur/15 (2 marks)

**Question:** What are three items to be learned for an RBF network? Difference to other NNs, Pros/cons?

**Model answer:** Three items to be learned are centers, weights, and biases. RBFN consists of a single hidden layer and a linear output layer. NN can have multiple hidden layers and a linear or non-linear output layer. Pros: RBFN is a universal approximator and it is easy to add more centers. Con: The bias is not unique.

_Marking stance: lenient. Full marks: the three learned items (centers, weights, biases) plus a correct difference or pro/con of RBFN in any wording. Part marks: two of the three items, or a vague comparison or pro/con. No marks for wrong or off-topic content; extra incorrect remarks do not cost marks unless they contradict the main idea._

- **P1** (1): Names the three items learned in an RBF network: centers, weights, and biases (in any wording, e.g. centre positions, output weights, bias term). _Partial: Half if two of the three items are given correctly._
- **P2** (1): Gives a difference from other NNs and/or a pro or con of RBFN, e.g. single hidden layer with linear output (vs. multiple hidden layers/non-linear output), universal approximator, easy to add centers, or bias not unique. _Partial: Half if only a vague or partial comparison/pro/con is given, or only one of difference or pros/cons is mentioned very briefly._


## digiklausur/16 (2 marks)

**Question:** Describe how learning based on k-nearest neighbors works, use pseudo code!

**Model answer:** Add the new data to the members of colored or classified old data, construct a sphere with k nearest data points, find the class or color which has the maximum vote and assign the new data to the class which has the maximum vote in an unsupervised manner.

_Marking stance: lenient. Full marks for a description (pseudo-code or plain steps) that finds the k nearest labelled points to the new point and assigns the majority class. Give 1 mark if the answer is vague or misses one key part (neighbour search or the vote). Give 0 if it is off-topic or describes a different method. Ignore the model answer's word "unsupervised"; do not penalise for it._

- **P1** (2): Core idea of k-NN: a new data point is compared with labelled/classified stored data, its k nearest points (neighbours by distance) are found, and the new point is assigned the class with the majority vote among them. Pseudo-code or step-by-step description in any wording is fine. _Partial: 1 mark if only part is given, e.g. finds nearest neighbours but no voting/class assignment, or a vague description of classifying by similar known data._


## digiklausur/17 (2 marks)

**Question:** Explain the Bias Variance Dilemma!

**Model answer:** Bias-variance dilemma is a principle supervised learning problem. The dilemma arises due to the variance of data and bias of model. When there is high bias, the model fits the training data perfectly but suffers from high variance, when the bias is low the variance reduces but the model doesn’t fit the data well. This dilemma makes the generalizability difficult to achieve.

_Marking stance: lenient. Full marks for saying in any wording that bias and variance pull against each other and that this makes good generalization hard. Give part marks for an answer that describes only bias or only variance, or one that is vague but on topic. Give no marks for an unrelated or wrong answer._

- **P1** (1): States the tradeoff: high bias (simple/underfitting model) goes with low variance and low bias (flexible model) goes with high variance, so reducing one tends to increase the other. Wording may be informal. The model answer's own wording (high bias gives a perfect training fit and high variance) is also accepted. _Partial: Half if only bias or only variance is described, or the trade-off is stated vaguely without saying how they relate._
- **P2** (1): Links the tradeoff to fit and generalization: it is hard to get a model that fits the training data well and also generalizes to new data (over/underfitting). _Partial: Half if it mentions only fit to the data or only generalization, or is vague._


## digiklausur/2 (2 marks)

**Question:** Define the mathematical model of a neuron, use the appropriate technical terms!

**Model answer:** Mathematical model of a neuron consists of a set of synapses or connecting links where each link is characterized by a weight, an adder function (linear combiner), which computes the weighted sum (local field) of the inputs plus some bias and an activation function (squashing function) for limiting the amplitude of a neuron’s output.

_Marking stance: lenient. Full marks for stating, in any wording, that inputs are weighted, summed with a bias, and passed through an activation function that limits the output. Give part marks for answers that are on the right track but vague or missing one part, such as no bias or no role for the activation. Give no marks for answers unrelated to weighted sum plus activation. Exact technical terms are not required._

- **P1** (1): Inputs are connected via synapses/links, each with a weight, and an adder (linear combiner) computes the weighted sum of the inputs plus a bias (local field). _Partial: Half if only weighted inputs or only the sum is mentioned, without weights/bias clearly described._
- **P2** (1): An activation (squashing) function is applied to the sum to limit the amplitude of the neuron's output. _Partial: Half if an activation function is named but its role is not given, or the role is described vaguely._


## digiklausur/3 (2 marks)

**Question:** Assume you want to binary classify linear separable data point using a perceptron. Write down the learning algorithm in pseudo code!

**Model answer:** Label the data with positive and negative (+/-) labels, initialize the weights randomly, apply (simplified) update rule: Dw = eta*x(n) if <w,x> <= 0, repeat on all epochs till the weights don’t change much. The algorithm will converge as the data is linearly separable.

_Marking stance: lenient. Full marks for pseudo-code (any wording) that initializes weights, loops over the data updating weights on misclassified points with a learning-rate times x rule, and stops when weights stop changing. Give part marks for a right-track but vague or incomplete algorithm, such as an update step without the misclassification condition. Give no marks for answers that are off-topic or describe something other than the perceptron learning rule. Exact syntax and the convergence remark are not required._

- **P1** (0.5): Setup: labels the data as positive/negative classes and initializes the weights (e.g. randomly or to zero). _Partial: Only one of labelling or initializing weights mentioned._
- **P2** (1): Loop with update rule: repeatedly goes over the data points (epochs) and, for a misclassified point (e.g. <w,x> <= 0 for the correct class), updates the weights by adding eta times x (w += eta*x, or sign/label-adjusted equivalent). _Partial: Has a loop and an update on errors but the rule is vague or incomplete._
- **P3** (0.5): Stopping: repeats until weights no longer change (or no misclassifications), and may note convergence because the data is linearly separable. _Partial: Vague stopping idea such as a fixed number of epochs._


## digiklausur/4 (2 marks)

**Question:** Explain classification and regression; what is the difference?

**Model answer:** Classification is a task of mapping data to discrete labels while regression is a task which maps data to a continuous function or real values. Error in classification is the number of misclassifications while in regression is the summed distance between the true and predicted values.

_Marking stance: lenient. Full marks for stating that classification outputs discrete labels and regression outputs continuous/real values, in any wording. Give half marks for vague but related answers (e.g. 'classification sorts things, regression predicts numbers'). Error measures (misclassification count vs summed distance) are optional extras; no marks for wrong or off-topic answers._

- **P1** (1): Says classification maps data/inputs to discrete labels or categories (classes). _Partial: Half if only vaguely says classification is about categories/predicting a class without clear contrast._
- **P2** (1): Says regression maps data/inputs to continuous or real-valued outputs, so the difference is discrete vs continuous output. _Partial: Half if regression is described as predicting numbers/values but without clearly contrasting with classification._


## digiklausur/5 (2 marks)

**Question:** Write down the SOM learning in pseudo code.

**Model answer:** Arrange the weights in the required topology according to the problem. Initialize the weights randomly such that all the weights are different. Sample the input from the input space. Similarity matching: match the input to a neuron in the topological lattice which becomes the winning neuron. Update the weights of the winning neuron and its neighbours determined by the neighbourhood function. Reduce the neighbourhood and decay the learning rate and share radius. If ordering and convergence are complete, stop. Else continue sampling from the input space.

_Marking stance: lenient. Full marks for a pseudo-code (or step list) in any wording that has initialise, sample input, find winning neuron, update winner and neighbours, and loop until done. Give part marks if the answer is on the right track but misses a major stage or is vague. Give no marks for an unrelated algorithm. Do not penalise missing details such as decaying the radius, or syntax._

- **P1** (1): Setup and sampling: weights arranged in a lattice/topology and initialised randomly, then an input is sampled from the input space (in a loop). _Partial: Half if only initialisation or only sampling is given._
- **P2** (1): Core iteration: find the winning neuron by matching the input to the closest neuron, update the winner and its neighbours using a neighbourhood function, shrink neighbourhood/learning rate, and repeat until convergence. _Partial: Half if the winner is found and updated but neighbours, shrinking, or the repeat/stop step is missing._


## digiklausur/6 (2 marks)

**Question:** Give the basic idea of an SVM using the correct terminology!

**Model answer:** SVMs are linear learnable machines in the simplest case. It uses a decision boundary with maximum margin to classify the data into different classes. The data points which are near the decision boundary are called support vectors and the margin is determined based on these points. Kernels are used to separate non-linearly separable data and the algorithm is solved by using Quadratic Programming.

_Marking stance: lenient. Full marks: the answer says SVM separates classes with a maximum-margin decision boundary, and mentions support vectors or kernels in any wording. Part marks: a vague answer, e.g. just "separates classes with a line" or only naming one idea loosely. No marks for wrong or off-topic answers. Extra remarks do not lose marks unless they contradict the core idea._

- **P1** (1): States the core idea: SVM is a (linear) classifier that separates classes with a decision boundary (hyperplane) chosen to maximise the margin. _Partial: Half if it mentions a decision boundary/separating classes but not maximum margin (or vice versa)._
- **P2** (1): Mentions support vectors (the data points closest to the boundary that determine the margin) and/or kernels for non-linearly separable data (optionally quadratic programming). _Partial: Half if only vaguely refers to points near the boundary or to handling non-linear data, without the terms._


## digiklausur/7 (2 marks)

**Question:** What role does the method of steepest decent have when learning a network?

**Model answer:** Steepest descent is used to update the weights in a NN during the learning phase. It helps to navigate the cost function and find the parameters for which the cost is minimum. The weights are updated in the direction of the steepest descent which is in a direction opposite to the gradient vector. This method could suffer from local minima and may become unstable.

_Marking stance: lenient. Full marks for saying steepest descent updates the weights to reduce the cost function and that it moves against the gradient, in any wording. Give half marks for vague answers, e.g. "it helps the network find the best weights" without the gradient idea. Mention of local minima or instability is optional and not needed for full marks._

- **P1** (1): Steepest descent is used to update the weights/parameters of the network during learning (training), in order to minimise the cost/error function. _Partial: Half if only says it is used in learning/optimisation without mentioning weight updates or minimising cost._
- **P2** (1): Weights are moved in the direction opposite to the gradient (downhill, direction of steepest decrease of the cost). _Partial: Half if mentions using the gradient or slope but direction is vague._


## digiklausur/8 (2 marks)

**Question:** Define: a hypothesis $h \in H$ shatters a dataset $A \subseteq X \Leftrightarrow \ldots$

**Model answer:** For all 2^N possible binary labeling of every data, if a hypothesis h splits the positive data from the negative data with no error, then it means that the hypothesis h shatters the dataset A.

_Marking stance: lenient. Full marks for saying that, for every possible labeling (2^N) of the dataset, the hypothesis can separate positive from negative points with no error, in any wording. Give 1 mark if only one half is clear (no-error separation, or all labelings) or the wording is vague. Give 0 if the answer is unrelated or contradicts the idea (e.g. only one labeling is classified correctly)._

- **P1** (2): States that h shatters A if, for every possible labeling of the points in A (all 2^N positive/negative assignments), h can classify them correctly, i.e. separate positives from negatives with no error. _Partial: 1 mark if only partly stated: e.g. h separates positives from negatives without error but 'all possible labelings' is missing, or all labelings is mentioned but the no-error separation is vague._


## digiklausur/9 (2 marks)

**Question:** Write down and explain the Widrow-Hoff learning rule!

**Model answer:** The adjustment made to a synaptic weight of a neuron is proportional to the product of the error signal and the input signal of the synapse in question. The rule is derived from the steepest descent method.

_Marking stance: lenient. Full marks: weight change proportional to error times input, plus mention that it comes from steepest/gradient descent (error minimisation), in any wording. Part marks for vague but relevant answers, e.g. a weight update depending on error only, or on minimising error without naming the method. No marks for unrelated rules (e.g. Hebbian only) or empty answers._

- **P1** (1): States the rule: the weight change of a synapse is proportional to the product of the error signal and the input signal at that synapse (Δw = η · e · x, or equivalent). _Partial: Half if only mentions error and input without the product/proportionality, or gives a vague update formula._
- **P2** (1): Explains that the rule is derived from / is based on steepest (gradient) descent, i.e. minimising the error (e.g. squared error / LMS). _Partial: Half if only says it reduces or minimises error without linking to gradient/steepest descent._
