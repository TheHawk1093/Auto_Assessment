# digiklausur: harsh rubrics

Marks per point add up to the question total.

## digiklausur/1 (2 marks)

**Question:** Give a definition for the term "artificial neural network" and mention, how it resembles the human brain!

**Model answer:** A neural network is a massively parallel distributed processor which is made up of simple processing units. It has a natural propensity for storing experiential knowledge. Neural networks resemble the brain in two aspects; knowledge is acquired by the network from its environment through a learning process, interneuron connection strength known as synaptic weights are used to store the acquired knowledge.

_Marking stance: harsh. Each of the four elements must be stated explicitly and correctly; vague wording like 'it works like a brain' earns nothing. The term 'synaptic weights' (connection strengths between neurons) is required for P4, and 'learning process' with 'environment' for P3. A wrong statement within a point cancels that point._

- **P1** (0.5): Definition: a neural network is a massively parallel distributed processor made up of simple processing units (both 'massively parallel distributed' and 'simple processing units' stated). _Partial: Only one of the two parts (parallel distributed processor OR simple processing units) stated precisely._
- **P2** (0.5): Definition: it has a natural propensity for storing experiential knowledge and making it available for use.
- **P3** (0.5): Resemblance 1: knowledge is acquired by the network from its environment through a learning process.
- **P4** (0.5): Resemblance 2: interneuron connection strengths, known as synaptic weights, are used to store the acquired knowledge (term 'synaptic weights' required).


## digiklausur/10 (2 marks)

**Question:** Explain back propagation, use the correct technical terms!

**Model answer:** Backpropagation lowers the error of a MLP level by level recursively backwards. It back propagates an error from the last layer to the first layer by updating the weights. The updates are determined by the local gradient at each level which is computed by partial derivatives of the error and chain rule.

_Marking stance: harsh. Full marks need all four elements stated explicitly with the correct terms: error reduction via weight updates, backward layer-by-layer direction (output to input), local gradient, and partial derivatives plus chain rule. Vague wording such as 'it goes back and fixes things' earns nothing for that point. Any wrong statement inside a point (e.g. propagating forward, first to last layer) cancels that point. Total is 2 marks, 0.5 per point; no half points within a point._

- **P1** (0.5): States that backpropagation lowers/minimises the error (loss) of a multilayer perceptron (MLP / neural network) by updating its weights.
- **P2** (0.5): States that the error is propagated backwards, from the last (output) layer to the first layer, level by level / recursively.
- **P3** (0.5): States that the weight updates are determined by the local gradient at each layer/level.
- **P4** (0.5): States that the local gradient is computed using partial derivatives of the error and the chain rule (both terms named). _Partial: Only one of 'partial derivatives' or 'chain rule' named correctly: no credit; both required._


## digiklausur/11 (2 marks)

**Question:** When learning using steepest descent, explain the role of the learning rate? What is a danger?

**Model answer:** Learning rate controls the speed of the convergence. When the learning rate is low, the convergence is overdamped and slow. When the learning rate is high, the convergence is underdamped and follows a zigzagging path. When the learning rate exceeds a critical value learning becomes unstable.

_Marking stance: harsh. Full marks need all four elements stated explicitly: role in convergence speed, low rate = slow/overdamped, high rate = underdamped/zigzag, and instability above a critical value. Vague statements such as 'too big is bad' earn nothing. A wrong statement within a point (e.g. low rate causes instability) cancels that point. Part marks only where more than half is stated precisely, as specified per point._

- **P1** (0.5): States that the learning rate controls the speed of convergence (step size of the steepest descent updates / how fast learning converges).
- **P2** (0.5): States that a low learning rate gives slow convergence, described as overdamped. _Partial: Half (0.25) if only 'slow' is stated without 'overdamped'._
- **P3** (0.5): States that a high learning rate gives underdamped convergence with a zigzagging/oscillating path. _Partial: Half (0.25) if only zigzag/oscillation is stated without 'underdamped'._
- **P4** (0.5): States the danger: if the learning rate exceeds a critical value, learning becomes unstable (diverges). _Partial: Half (0.25) if instability/divergence is stated without reference to a critical value or threshold._


## digiklausur/12 (2 marks)

**Question:** How does a Reduced Boltzman Machine work (main idea)?

**Model answer:** The reduced Boltzmann machine is a bi-parted graph which works by flipping the states of binary neurons based on a probability determined by the activation produced at the neuron. Neurons are arranged in a visible and a hidden layer in a recurrent fashion. There are two states involved called the clamped state in which the visible neuron is connected to the input and a free running state in which both layers run free.

_Marking stance: harsh. Each of the four elements must be stated explicitly with the correct terms (bipartite, visible/hidden, binary, probability from activation, clamped, free-running). Vague wording such as "it learns patterns" earns nothing for a point. A wrong statement within a point (e.g. deterministic updates, or connections within a layer) cancels that point._

- **P1** (0.5): States that the RBM is a bipartite (bi-parted) graph with a visible layer and a hidden layer of neurons (no connections within a layer), with recurrent/symmetric connections between the layers. _Partial: Half only if bipartite/visible-and-hidden layers are named but the recurrent connection between them is missing._
- **P2** (0.5): States that the neurons are binary and work by flipping/changing their states (on/off).
- **P3** (0.5): States that the flip of a neuron's state is probabilistic (stochastic), with the probability determined by the neuron's activation.
- **P4** (0.5): States the two phases/states: the clamped state, where the visible neurons are connected to (clamped to) the input, and the free-running state, where both visible and hidden layers run freely. _Partial: Half if only one of the two states is correctly described, or both are named without explanation._


## digiklausur/13 (2 marks)

**Question:** Define: Echo State Network (ESN), how are they different to FF NNs?

**Model answer:** Echo State Network is a type of Recurrent Neural Network and has at least one cyclic (feedback) connection. Only the weights of the output layers are updated while learning. ESN consists of feedback connections while a FF NN does not. ESN can approximate dynamic systems while FF NN cannot.

_Marking stance: harsh. Each point needs an explicit, correct statement using the terms recurrent/feedback (cyclic) connection, output layer weights, and dynamic systems. Vague wording (e.g. "ESN has memory", "ESN is more complex") earns nothing, and a wrong statement inside a point (e.g. saying all weights are trained, or that ESN is feed-forward) cancels that point. Total is the sum of points earned, out of 2._

- **P1** (0.5): States that an ESN is a type of Recurrent Neural Network (RNN) that has at least one cyclic/feedback connection (both the RNN classification and the cyclic/feedback connection must be stated). _Partial: Only one of the two (RNN, or cyclic/feedback connection) stated precisely earns no marks; both are required._
- **P2** (0.5): States that only the weights of the output layer are updated/trained during learning (other weights are not trained).
- **P3** (0.5): Difference 1: ESN has feedback (recurrent) connections whereas a FF NN does not (signals flow only forward).
- **P4** (0.5): Difference 2: ESN can approximate dynamic systems whereas a FF NN cannot.


## digiklausur/14 (2 marks)

**Question:** Describe: the structure on an CNN.

**Model answer:** Convolutional Neural Network consists of many layers such as a convolutional layer that has kernels which convolve over the input image, an activation layer (ReLU activation), pooling layer (max or average pooling), and one or more fully connected layers followed by softmax layer.

_Marking stance: harsh. Each of the four elements must be explicit and use the correct term: convolutional layer with kernels, ReLU activation, pooling (max/average), fully connected layers then softmax. Vague wording such as "layers that process the image" earns nothing for that point; part marks only where the point is more than half stated. A wrong statement (e.g. softmax placed before the convolution, or pooling described as something else) cancels that point._

- **P1** (0.5): States that a CNN has a convolutional layer in which kernels (filters) convolve over the input image. _Partial: Convolutional layer named but kernels/convolving over the input not stated._
- **P2** (0.5): States that an activation layer follows, using ReLU activation. _Partial: Activation layer named without ReLU._
- **P3** (0.5): States a pooling layer, with max or average pooling named. _Partial: Pooling layer named without max/average type._
- **P4** (0.5): States one or more fully connected layers followed by a softmax layer (output). _Partial: Fully connected layers named without softmax, or softmax without fully connected layers._


## digiklausur/15 (2 marks)

**Question:** What are three items to be learned for an RBF network? Difference to other NNs, Pros/cons?

**Model answer:** Three items to be learned are centers, weights, and biases. RBFN consists of a single hidden layer and a linear output layer. NN can have multiple hidden layers and a linear or non-linear output layer. Pros: RBFN is a universal approximator and it is easy to add more centers. Con: The bias is not unique.

_Marking stance: harsh. Full marks need every element stated explicitly with the correct terms (centers, weights, biases; single hidden layer; linear output layer; universal approximator; bias not unique). Vague or generic statements earn nothing for that point, and a wrong statement or wrong extra item in a point cancels it. Part marks only where the partial_credit condition is clearly met; total is capped at 2._

- **P1** (0.5): States all three items to be learned: centers, weights and biases (all three named). _Partial: Two of the three items named correctly and none wrong earns half._
- **P2** (0.5): Difference to other NNs: RBFN has a single hidden layer with a linear output layer, whereas a general NN can have multiple hidden layers and a linear or non-linear output layer. _Partial: Only one side stated precisely (RBFN single hidden layer + linear output, or NN multiple hidden layers/non-linear output) earns half._
- **P3** (0.5): Pros: states that RBFN is a universal approximator and that it is easy to add more centers. _Partial: One of the two pros stated precisely earns half._
- **P4** (0.5): Con: states that the bias is not unique.


## digiklausur/16 (2 marks)

**Question:** Describe how learning based on k-nearest neighbors works, use pseudo code!

**Model answer:** Add the new data to the members of colored or classified old data, construct a sphere with k nearest data points, find the class or color which has the maximum vote and assign the new data to the class which has the maximum vote in an unsupervised manner.

_Marking stance: harsh. Full marks need all four steps stated explicitly, in order and as pseudo-code: place new point among labelled data, take the k nearest points, majority vote on class, assign the class. Vague wording (e.g. "looks at neighbours") earns nothing for that point, and a wrong statement in a step cancels it. The terms k nearest points and maximum/majority vote must appear; part marks only where clearly more than half of a point is precise._

- **P1** (0.5): States that the new (unclassified) data point is added to/compared with the existing labelled (classified/colored) training data, e.g. by computing distances to the labelled points.
- **P2** (0.5): Explicitly selects the k nearest data points (the neighbourhood, e.g. a sphere/region containing the k nearest points) around the new point, with k named as the number of neighbours.
- **P3** (0.5): Counts the class labels (colors) among the k neighbours and finds the class with the maximum vote (majority voting).
- **P4** (0.5): Assigns the new data point to the class with the maximum vote, and presents the steps as pseudo-code in the correct order (add/compare, select k nearest, vote, assign). _Partial: Correct assignment step stated but steps are not given as ordered pseudo-code, or order is wrong: 0.25_


## digiklausur/17 (2 marks)

**Question:** Explain the Bias Variance Dilemma!

**Model answer:** Bias-variance dilemma is a principle supervised learning problem. The dilemma arises due to the variance of data and bias of model. When there is high bias, the model fits the training data perfectly but suffers from high variance, when the bias is low the variance reduces but the model doesn’t fit the data well. This dilemma makes the generalizability difficult to achieve.

_Marking stance: harsh. Full marks need all four elements stated explicitly with the terms bias, variance, and generalisation; the trade-off must be stated in both directions. Vague wording such as 'a balance of errors' earns nothing for that point. A wrong statement within a point (e.g. low bias gives high variance with no trade-off, or swapping bias and variance) cancels that point. Note that the model answer's high-bias/low-bias wording is unusual; mark the student's trade-off direction for consistency with the model answer's logic of an inverse relation between bias and variance._

- **P1** (0.5): States that the bias-variance dilemma is a problem/principle in supervised learning, arising from the bias of the model and the variance (of the model's output/with respect to the data), i.e. both bias and variance are named as the two error sources.
- **P2** (0.5): States that high bias (as worded in the model answer) goes with fitting the training data very well but high variance.
- **P3** (0.5): States that low bias goes with reduced variance but the model does not fit the data well; i.e. reducing one increases the other (a trade-off).
- **P4** (0.5): States that this dilemma makes generalisation (generalizability) difficult to achieve, using the term generalisation.


## digiklausur/2 (2 marks)

**Question:** Define the mathematical model of a neuron, use the appropriate technical terms!

**Model answer:** Mathematical model of a neuron consists of a set of synapses or connecting links where each link is characterized by a weight, an adder function (linear combiner), which computes the weighted sum (local field) of the inputs plus some bias and an activation function (squashing function) for limiting the amplitude of a neuron’s output.

_Marking stance: harsh. Full marks need all four elements stated explicitly with the correct terms: synapses with weights, adder/linear combiner (weighted sum), bias, and activation (squashing) function limiting output amplitude. Vague wording such as "inputs are multiplied and processed" earns nothing for that point. A wrong statement within a point (e.g. the activation function described as computing the sum) cancels that point._

- **P1** (0.5): States that the neuron model has a set of synapses (connecting links), each characterized by its own weight (synaptic weight). _Partial: Half only if synapses/links are named but weights are not stated, or vice versa; actually 0 if either term is missing or wrong._
- **P2** (0.5): States an adder (linear combiner) that computes the weighted sum of the inputs (the local field / induced local field).
- **P3** (0.5): States that a bias is added to the weighted sum of the inputs.
- **P4** (0.5): States an activation function (squashing function) that limits the amplitude of the neuron's output.


## digiklausur/3 (2 marks)

**Question:** Assume you want to binary classify linear separable data point using a perceptron. Write down the learning algorithm in pseudo code!

**Model answer:** Label the data with positive and negative (+/-) labels, initialize the weights randomly, apply (simplified) update rule: Dw = eta*x(n) if <w,x> <= 0, repeat on all epochs till the weights don’t change much. The algorithm will converge as the data is linearly separable.

_Marking stance: harsh. Full marks need all four elements to be explicit and correct: labelling and initialisation, the update rule Δw = eta*x(n) with the condition <w,x> <= 0, the epoch loop over all points, and the stopping condition with the linear-separability convergence reason. Vague wording such as "adjust the weights" earns nothing, and a wrong update rule or condition cancels P2. Ignore syntax; steps and their order matter._

- **P1** (0.5): Initialisation and labelling: data labelled with positive/negative (+/-) classes and the weights initialised (randomly) before training starts. _Partial: Half only if just one of labelling or weight initialisation is stated explicitly._
- **P2** (0.75): Update rule stated correctly: for a misclassified point (<w,x> <= 0 for the positive-labelled/sign-adjusted sample x(n)), update weights with Δw = eta * x(n) (learning rate times input), i.e. update only on misclassified points. _Partial: Half if the update Δw = eta*x(n) is given but the misclassification condition (<w,x> <= 0) is missing or wrong, or vice versa._
- **P3** (0.4): Loop structure: the update is applied by iterating over all data points in repeated epochs, in a loop.
- **P4** (0.35): Stopping condition: repeat until the weights no longer change (or no misclassifications remain), and note that it converges because the data is linearly separable. _Partial: Half if only the stop condition or only the convergence reason is given._


## digiklausur/4 (2 marks)

**Question:** Explain classification and regression; what is the difference?

**Model answer:** Classification is a task of mapping data to discrete labels while regression is a task which maps data to a continuous function or real values. Error in classification is the number of misclassifications while in regression is the summed distance between the true and predicted values.

_Marking stance: harsh. Each point needs an explicit, correct statement using the terms discrete/labels, continuous/real values, number of misclassifications, and summed distance between true and predicted values. Vague wording (e.g. 'classification sorts things', 'regression predicts numbers' without continuous) earns nothing for that point. A wrong statement, such as swapping the two, cancels that point. The difference must come through in the answer; the error points are required, not optional._

- **P1** (0.5): Classification defined as mapping input data to discrete labels/classes (categories).
- **P2** (0.5): Regression defined as mapping input data to a continuous function / continuous real-valued outputs.
- **P3** (0.5): Error in classification is the number of misclassifications (count of wrongly labelled samples).
- **P4** (0.5): Error in regression is the summed distance (e.g. sum of differences/absolute or squared) between true and predicted values.


## digiklausur/5 (2 marks)

**Question:** Write down the SOM learning in pseudo code.

**Model answer:** Arrange the weights in the required topology according to the problem. Initialize the weights randomly such that all the weights are different. Sample the input from the input space. Similarity matching: match the input to a neuron in the topological lattice which becomes the winning neuron. Update the weights of the winning neuron and its neighbours determined by the neighbourhood function. Reduce the neighbourhood and decay the learning rate and share radius. If ordering and convergence are complete, stop. Else continue sampling from the input space.

_Marking stance: harsh. Steps must be explicit, correct and in order: initialise, sample, similarity match, update winner and neighbours, decay, loop until convergence. Vague wording (e.g. 'train the map') earns nothing; an error inside a step (e.g. updating only the losers, or no neighbourhood) cancels that step. Half marks only where clearly more than half of a point is stated precisely._

- **P1** (0.5): Initialisation: weights arranged in the required topology (lattice) and initialised randomly so that all weights are different. _Partial: Half (0.25) if only random initialisation or only topology is stated, not both._
- **P2** (0.5): Sampling and similarity matching: sample an input vector from the input space and match it to a neuron in the lattice (best match), which becomes the winning neuron. _Partial: Half (0.25) if sampling is stated but the winning neuron selection by similarity matching is missing, or vice versa._
- **P3** (0.5): Update: weights of the winning neuron AND its neighbours (determined by the neighbourhood function) are updated. _Partial: Half (0.25) if only the winner's weights are updated, or neighbours are mentioned without the neighbourhood function._
- **P4** (0.5): Shrinking and termination: neighbourhood is reduced and learning rate decayed; loop repeats from sampling until ordering and convergence are complete, then stop. _Partial: Half (0.25) if only the decay/shrinking or only the stopping/loop condition is stated._


## digiklausur/6 (2 marks)

**Question:** Give the basic idea of an SVM using the correct terminology!

**Model answer:** SVMs are linear learnable machines in the simplest case. It uses a decision boundary with maximum margin to classify the data into different classes. The data points which are near the decision boundary are called support vectors and the margin is determined based on these points. Kernels are used to separate non-linearly separable data and the algorithm is solved by using Quadratic Programming.

_Marking stance: harsh. Full marks need the maximum-margin decision boundary, support vectors (close points defining the margin), kernels for non-linear data, and quadratic programming, all with correct technical terms. Vague wording such as 'a line that separates data' without margin or terms earns nothing for that point. Any wrong statement inside a point (e.g. support vectors as the farthest points) cancels that point. Total is capped at 2._

- **P1** (0.75): States that an SVM is a linear learning machine (linear classifier) in the simplest case, which classifies data into classes using a decision boundary (hyperplane) with maximum margin. _Partial: Half if only the decision boundary/hyperplane is named, or only 'maximum margin' is stated without the decision boundary (clearly more than half required)._
- **P2** (0.5): States that the data points closest to the decision boundary are called support vectors, and that the margin is determined by these points. _Partial: Half if 'support vectors' is named but their role in determining the margin or their closeness to the boundary is missing._
- **P3** (0.5): States that kernels (kernel trick) are used to handle non-linearly separable data.
- **P4** (0.25): States that the SVM optimisation problem is solved using Quadratic Programming.


## digiklausur/7 (2 marks)

**Question:** What role does the method of steepest decent have when learning a network?

**Model answer:** Steepest descent is used to update the weights in a NN during the learning phase. It helps to navigate the cost function and find the parameters for which the cost is minimum. The weights are updated in the direction of the steepest descent which is in a direction opposite to the gradient vector. This method could suffer from local minima and may become unstable.

_Marking stance: harsh. Each point needs an explicit, correct statement; vague wording such as 'it improves the network' earns nothing. Saying the update is along the gradient (not opposite) or in the wrong direction cancels P3. Award 2 marks only if all four elements are stated precisely, using terms like weights, cost function, gradient vector and local minima._

- **P1** (0.5): States that steepest descent is used to update the weights/parameters of the network during the learning (training) phase.
- **P2** (0.5): States that its purpose is to navigate the cost function to find the parameters/weights for which the cost is minimum (minimises the cost function).
- **P3** (0.5): States that weights are updated in the direction of steepest descent, i.e. opposite to the gradient vector (negative gradient) of the cost function.
- **P4** (0.5): States a limitation: it can get stuck in local minima and/or may become unstable. _Partial: Only one of local minima or instability named correctly is sufficient for full marks; vague 'has problems' earns nothing._


## digiklausur/8 (2 marks)

**Question:** Define: a hypothesis $h \in H$ shatters a dataset $A \subseteq X \Leftrightarrow \ldots$

**Model answer:** For all 2^N possible binary labeling of every data, if a hypothesis h splits the positive data from the negative data with no error, then it means that the hypothesis h shatters the dataset A.

_Marking stance: harsh. Full marks need all three elements stated explicitly: all 2^N binary labelings, h splits positives from negatives, and with no error. Vague wording such as 'h classifies the data well' or 'h works on the dataset' earns nothing for that point. A wrong statement (e.g. only some labelings, or allowing errors) cancels the relevant point; part marks only where P1 is clearly more than half stated._

- **P1** (0.75): States that the condition must hold for ALL possible labelings of the data points in A, i.e. all 2^N binary (positive/negative) labelings for N data points. _Partial: Says 'all labelings' or 'every labeling' but does not give 2^N or binary/positive-negative labels (or vice versa); 0.4_
- **P2** (0.75): States that for each such labeling there is a hypothesis h (in H) that separates/splits the positive data from the negative data.
- **P3** (0.5): States that the separation is with no error (zero misclassification, perfectly correct on every point of A).


## digiklausur/9 (2 marks)

**Question:** Write down and explain the Widrow-Hoff learning rule!

**Model answer:** The adjustment made to a synaptic weight of a neuron is proportional to the product of the error signal and the input signal of the synapse in question. The rule is derived from the steepest descent method.

_Marking stance: harsh. Full marks need both: the weight change proportional to error signal × input signal of that synapse (formula in rough LaTeX is acceptable if its meaning is correct), and the statement that it comes from steepest descent. Vague wording such as 'weights are updated based on error' earns nothing for P1. A wrong statement (e.g. proportional to the output only, or derived from another method) cancels that point._

- **P1** (1): States that the weight adjustment (change in synaptic weight, Δw) is proportional to the product of the error signal and the input signal of that synapse (Δw_kj = η · e_k · x_j, with η as learning-rate/proportionality constant). Both the error signal and the synapse's input signal must be named as factors in the product. _Partial: Half only if the product form is clearly given but one factor (error or input) is imprecise or the proportionality is not stated; otherwise 0._
- **P2** (1): States that the rule is derived from the steepest descent (gradient descent) method, i.e. minimising the error/cost function by moving against its gradient.
