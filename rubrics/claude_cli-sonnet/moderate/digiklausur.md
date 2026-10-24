# digiklausur: moderate rubrics

Marks per point add up to the question total.

## digiklausur/1 (2 marks)

**Question:** Give a definition for the term "artificial neural network" and mention, how it resembles the human brain!

**Model answer:** A neural network is a massively parallel distributed processor which is made up of simple processing units. It has a natural propensity for storing experiential knowledge. Neural networks resemble the brain in two aspects; knowledge is acquired by the network from its environment through a learning process, interneuron connection strength known as synaptic weights are used to store the acquired knowledge.

_Marking stance: moderate. Full marks need a correct definition (parallel distributed processor of simple units that stores experiential knowledge) and both brain similarities (learning from environment; knowledge stored in synaptic weights/connection strengths). Give half of a point for a vague or incomplete version, such as one similarity only or missing key terms. Give no marks for wrong or off-topic statements, such as describing only biology with no network definition._

- **P1** (1): Definition: a neural network is a massively parallel distributed processor made up of simple processing units, with a natural propensity for storing experiential knowledge (and making it available for use). _Partial: Half if the definition is vague or gives only one element (e.g. just 'simple processing units' or 'parallel processor') or omits knowledge storage._
- **P2** (1): Resemblance to the brain: (a) knowledge is acquired from the environment through a learning process, and (b) interneuron connection strengths, called synaptic weights, store the acquired knowledge. _Partial: Half if only one of the two aspects is stated, or both are stated without the term 'synaptic weights' / connection strengths._


## digiklausur/10 (2 marks)

**Question:** Explain back propagation, use the correct technical terms!

**Model answer:** Backpropagation lowers the error of a MLP level by level recursively backwards. It back propagates an error from the last layer to the first layer by updating the weights. The updates are determined by the local gradient at each level which is computed by partial derivatives of the error and chain rule.

_Marking stance: moderate. Full marks: the answer says the error is propagated backwards from output to input layer, updating weights to reduce error, and that the updates come from gradients (partial derivatives) via the chain rule. Give part marks when one key term (e.g. chain rule, gradient) is missing or the wording is vague. Give no marks for wrong or off-topic descriptions, such as describing only the forward pass._

- **P1** (1): States that backpropagation reduces/minimises the error (loss) of a multilayer network (MLP) by propagating the error backwards from the last (output) layer to the first layer, layer by layer, and by updating the weights. _Partial: Half if only one of: error goes backwards layer by layer, or weights are updated to reduce error, or described vaguely._
- **P2** (1): Explains that the weight updates are determined by the local gradient at each layer, computed using partial derivatives of the error and the chain rule. _Partial: Half if gradients or derivatives are mentioned without the chain rule or local gradient (or the chain rule without gradients/partial derivatives)._


## digiklausur/11 (2 marks)

**Question:** When learning using steepest descent, explain the role of the learning rate? What is a danger?

**Model answer:** Learning rate controls the speed of the convergence. When the learning rate is low, the convergence is overdamped and slow. When the learning rate is high, the convergence is underdamped and follows a zigzagging path. When the learning rate exceeds a critical value learning becomes unstable.

_Marking stance: moderate. Full marks need both: the learning rate sets step size/speed of convergence (with low = slow, high = oscillating), and the danger that too large a rate (above a critical value) makes learning unstable/diverge. Give half for vague or incomplete versions of either idea, e.g. only 'too large is bad' or only zigzagging. Give nothing for wrong or unrelated statements, such as saying a higher rate always improves learning._

- **P1** (1): Role of the learning rate: it controls the step size / speed of convergence of steepest descent. Low rate gives slow (overdamped) convergence; high rate gives faster but oscillating/zigzagging (underdamped) convergence. _Partial: Half if only says it controls speed/step size without describing the effect of low or high values, or gives only one of the low/high effects vaguely._
- **P2** (1): Danger: if the learning rate exceeds a critical value, learning becomes unstable (diverges rather than converges). _Partial: Half if only mentions oscillation/zigzagging or overshooting for a large rate without stating instability/divergence._


## digiklausur/12 (2 marks)

**Question:** How does a Reduced Boltzman Machine work (main idea)?

**Model answer:** The reduced Boltzmann machine is a bi-parted graph which works by flipping the states of binary neurons based on a probability determined by the activation produced at the neuron. Neurons are arranged in a visible and a hidden layer in a recurrent fashion. There are two states involved called the clamped state in which the visible neuron is connected to the input and a free running state in which both layers run free.

_Marking stance: moderate. Full marks need the bipartite visible/hidden structure, stochastic binary neuron updates driven by activation probability, and the clamped vs free-running states. Give part marks for ideas stated vaguely or with only one half present. Give no marks for descriptions of other networks (e.g. feed-forward or Hopfield only) with none of these ideas. Different wording is fine._

- **P1** (0.75): Structure: a bipartite graph / two layers (visible and hidden) of binary neurons, connected recurrently (no connections within a layer). _Partial: Half if only layers named or only 'bipartite' without visible/hidden._
- **P2** (0.75): Core mechanism: neurons' binary states are flipped/set stochastically, with a probability determined by the neuron's activation. _Partial: Half if stochastic/binary mentioned but link to activation-based probability is missing or vague._
- **P3** (0.5): Two phases/states: clamped state (visible neurons connected to/fixed by the input) and free-running state (both layers run freely). _Partial: Half if only one of the two states is correctly described._


## digiklausur/13 (2 marks)

**Question:** Define: Echo State Network (ESN), how are they different to FF NNs?

**Model answer:** Echo State Network is a type of Recurrent Neural Network and has at least one cyclic (feedback) connection. Only the weights of the output layers are updated while learning. ESN consists of feedback connections while a FF NN does not. ESN can approximate dynamic systems while FF NN cannot.

_Marking stance: moderate. Full marks: P1 needs ESN named as a recurrent network with feedback/cyclic connections plus the output-only training; P2 needs the contrast with FF NNs (feedback vs none, and dynamic systems). Half marks for a point that is vague or has only one of its two ideas. Zero for a point that is wrong, e.g. calling an ESN feedforward or saying all weights are trained._

- **P1** (1): Defines ESN as a type of Recurrent Neural Network with at least one cyclic/feedback connection (recurrent connections), and says that only the output layer weights are trained/updated. _Partial: Half if only one of the two ideas (recurrent with feedback connections, or only output weights trained) is given, or the definition is vague._
- **P2** (1): Explains the difference from FF NNs: ESN has feedback (cyclic) connections while a FF NN does not, so an ESN can approximate dynamic systems while a FF NN cannot. _Partial: Half if only the feedback vs no-feedback contrast or only the dynamic-systems point is given, or the contrast is vague._


## digiklausur/14 (2 marks)

**Question:** Describe: the structure on an CNN.

**Model answer:** Convolutional Neural Network consists of many layers such as a convolutional layer that has kernels which convolve over the input image, an activation layer (ReLU activation), pooling layer (max or average pooling), and one or more fully connected layers followed by softmax layer.

_Marking stance: moderate. Full marks need the main layer types in a sensible order: convolution with kernels plus ReLU, then pooling, then fully connected layers with softmax. Give half a point where an element is missing or vague (e.g., 'filters' with no convolving idea, or no softmax). Give no marks for answers that describe a generic neural network without convolution or pooling._

- **P1** (1): Convolutional layer(s): uses kernels/filters that convolve over the input image (producing feature maps), followed by an activation layer such as ReLU. _Partial: Half if the convolutional layer is named but kernels/convolving is not mentioned, or if the activation (ReLU) is missing._
- **P2** (1): Pooling layer (max or average pooling), then one or more fully connected layers ending with a softmax output layer. _Partial: Half if only pooling or only the fully connected/softmax part is given, or if the order is clearly wrong._


## digiklausur/15 (2 marks)

**Question:** What are three items to be learned for an RBF network? Difference to other NNs, Pros/cons?

**Model answer:** Three items to be learned are centers, weights, and biases. RBFN consists of a single hidden layer and a linear output layer. NN can have multiple hidden layers and a linear or non-linear output layer. Pros: RBFN is a universal approximator and it is easy to add more centers. Con: The bias is not unique.

_Marking stance: moderate. Full marks need the three items (centers, weights, biases), the single-hidden-layer/linear-output difference, and at least one valid pro and con. Give part marks for incomplete or vague statements, such as two items listed, only one side of the difference, or only pros. A wrong statement loses only that point's marks; give no marks for off-topic answers._

- **P1** (0.5): Names the three items to be learned: centers, weights, and biases. _Partial: Two of the three items named correctly._
- **P2** (0.75): Difference to other NNs: an RBFN has a single hidden layer and a linear output layer, whereas other NNs can have multiple hidden layers and a linear or non-linear output layer. _Partial: Only one side stated (e.g. single hidden layer) or the output layer difference is vague._
- **P3** (0.75): Gives at least one pro and one con of RBFN. Pros: universal approximator, easy to add more centers. Con: the bias is not unique. _Partial: Only a pro or only a con given, or points are vague._


## digiklausur/16 (2 marks)

**Question:** Describe how learning based on k-nearest neighbors works, use pseudo code!

**Model answer:** Add the new data to the members of colored or classified old data, construct a sphere with k nearest data points, find the class or color which has the maximum vote and assign the new data to the class which has the maximum vote in an unsupervised manner.

_Marking stance: moderate. Full marks: ordered steps (pseudo-code or clear sequence) that find the k nearest labelled points to the new point and assign the class with the most votes among them. Part marks: one step is vague or missing a key term such as k, nearest or vote. No marks: wrong algorithm (e.g. clustering without labels or no neighbours) or off-topic. The model answer's word 'unsupervised' is a slip, so do not require it or penalise its absence._

- **P1** (1): Describes the setup and neighbour step: the new data point is placed among the existing labelled (classified/coloured) data, and its k nearest data points (neighbours, by distance) are found/selected. _Partial: Half if neighbours are mentioned but k or distance/nearest is vague, or the labelled training data is not mentioned._
- **P2** (1): Describes the decision step: a majority vote among the k neighbours' classes is taken, and the new point is assigned to the class with the maximum votes. Steps are presented as pseudo-code (or clearly ordered steps). _Partial: Half if the voting/assignment is vague (e.g. 'assign to the most similar class') or no pseudo-code/ordered steps are given._


## digiklausur/17 (2 marks)

**Question:** Explain the Bias Variance Dilemma!

**Model answer:** Bias-variance dilemma is a principle supervised learning problem. The dilemma arises due to the variance of data and bias of model. When there is high bias, the model fits the training data perfectly but suffers from high variance, when the bias is low the variance reduces but the model doesn’t fit the data well. This dilemma makes the generalizability difficult to achieve.

_Marking stance: moderate. Full marks: the trade-off between bias and variance is stated, both sides are explained (close fit with high variance vs. lower variance with poor fit), and generalization difficulty is mentioned. Part marks for vague or one-sided explanations or a minor error. No marks for answers that do not link bias and variance as a trade-off. Accept the standard textbook wording (low bias/high variance = overfitting) as equivalent if the trade-off is correct._

- **P1** (0.5): States that the bias-variance dilemma is a trade-off in supervised learning between model bias and variance (of the model's fit to the data): reducing one tends to increase the other. _Partial: Half if only mentions bias and variance without the trade-off/opposing relationship._
- **P2** (1): Explains the two sides: high bias/low variance... specifically, per the model answer, one extreme fits the training data very closely but with high variance, while the other has lower variance but the model does not fit the data well (underfits). _Partial: Half if only one side is explained correctly or the description is vague._
- **P3** (0.5): States the consequence: the trade-off makes good generalization difficult to achieve. _Partial: Half if generalization is mentioned only vaguely (e.g. 'performs badly on new data') without the link to the dilemma._


## digiklausur/2 (2 marks)

**Question:** Define the mathematical model of a neuron, use the appropriate technical terms!

**Model answer:** Mathematical model of a neuron consists of a set of synapses or connecting links where each link is characterized by a weight, an adder function (linear combiner), which computes the weighted sum (local field) of the inputs plus some bias and an activation function (squashing function) for limiting the amplitude of a neuron’s output.

_Marking stance: moderate. Full marks need all three components: weighted synapses, an adder (linear combiner) giving the weighted sum plus bias, and an activation (squashing) function limiting output amplitude. Give part marks when a component is vague or one element (e.g. bias) is missing. Give no marks for a biological description of a neuron or wrong components. Different wording is fine if the technical terms are used._

- **P1** (0.5): Synapses / connecting links, each characterized by a weight (applied to the inputs). _Partial: Mentions inputs or connections but not weights._
- **P2** (1): Adder / linear combiner computes the weighted sum of the inputs (local field) plus a bias. _Partial: Weighted sum given but bias missing, or adder named without saying what it computes._
- **P3** (0.5): Activation (squashing) function limits the amplitude of the neuron's output. _Partial: Names an activation function but does not say it limits/squashes the output._


## digiklausur/3 (2 marks)

**Question:** Assume you want to binary classify linear separable data point using a perceptron. Write down the learning algorithm in pseudo code!

**Model answer:** Label the data with positive and negative (+/-) labels, initialize the weights randomly, apply (simplified) update rule: Dw = eta*x(n) if <w,x> <= 0, repeat on all epochs till the weights don’t change much. The algorithm will converge as the data is linearly separable.

_Marking stance: moderate. Full marks need pseudo-code with initialised weights, the perceptron update (Δw = η·x applied only to misclassified points), and repetition over epochs until the weights stop changing. Give part marks when one element is vague or missing, e.g. no learning rate, no misclassification condition, or no stopping criterion. Give no marks for answers describing a different algorithm or unrelated content. Steps and their order matter more than syntax._

- **P1** (0.5): Setup: labelled data with two classes (+/- or +1/-1) and weights initialised (e.g. randomly or to zero). _Partial: Only one of labels or weight initialisation mentioned._
- **P2** (1): Update rule: for a misclassified point (e.g. <w,x> <= 0 for the correctly signed/simplified input), update the weights by adding eta*x (Δw = η·x, with learning rate eta; sign by label is fine). _Partial: Update given but without learning rate, or without the misclassification condition, or with a minor error._
- **P3** (0.5): Loop structure: repeat over all data points/epochs until weights no longer change (or no misclassifications / converged); may note convergence since data is linearly separable. _Partial: Repeat mentioned but no stopping criterion._


## digiklausur/4 (2 marks)

**Question:** Explain classification and regression; what is the difference?

**Model answer:** Classification is a task of mapping data to discrete labels while regression is a task which maps data to a continuous function or real values. Error in classification is the number of misclassifications while in regression is the summed distance between the true and predicted values.

_Marking stance: moderate. Full marks need both tasks correctly defined (discrete labels vs continuous/real values), the contrast made clear, and the differing error measures given. Award part marks for vague wording or for giving only one error measure. Give no marks for a swapped or wrong definition; each point is judged on its own._

- **P1** (0.5): Classification defined as mapping data/inputs to discrete labels (classes or categories). _Partial: Half if only vaguely stated (e.g. 'sorting into groups') without 'discrete' or labels/classes._
- **P2** (0.5): Regression defined as mapping data/inputs to continuous values (real-valued outputs or a continuous function). _Partial: Half if only vaguely stated (e.g. 'predicts numbers') without 'continuous' or real values._
- **P3** (0.5): States the difference in output type: discrete labels for classification versus continuous/real values for regression, as an explicit contrast. _Partial: Half if the contrast is only implied by the two definitions or is vague._
- **P4** (0.5): Error measure differs: classification error is the number of misclassifications; regression error is the summed distance (e.g. sum of differences/squared errors) between true and predicted values. _Partial: Half if only one of the two error measures is correct or both are vague._


## digiklausur/5 (2 marks)

**Question:** Write down the SOM learning in pseudo code.

**Model answer:** Arrange the weights in the required topology according to the problem. Initialize the weights randomly such that all the weights are different. Sample the input from the input space. Similarity matching: match the input to a neuron in the topological lattice which becomes the winning neuron. Update the weights of the winning neuron and its neighbours determined by the neighbourhood function. Reduce the neighbourhood and decay the learning rate and share radius. If ordering and convergence are complete, stop. Else continue sampling from the input space.

_Marking stance: moderate. Full marks need the steps in a sensible order: initialise and sample, find the winner by similarity matching, update the winner and its neighbours using the neighbourhood function, reduce neighbourhood and learning rate, and repeat until convergence. Give part marks for steps that are vague or only partly stated. Give no marks for steps that are wrong (e.g. backpropagation or error-correction updates) or off-topic; pseudo-code syntax is not important._

- **P1** (0.5): Setup and input step: arrange weights/neurons in a topology (lattice), initialise weights randomly (different values), and sample an input vector from the input space. _Partial: Half if only initialisation or only sampling is given, or topology/random initialisation is vague._
- **P2** (0.5): Similarity matching: find the winning neuron (best matching unit) in the lattice for the sampled input. _Partial: Half if matching is mentioned vaguely without naming the winning neuron._
- **P3** (0.5): Update the weights of the winning neuron and its neighbours, with the neighbourhood determined by a neighbourhood function. _Partial: Half if only the winner is updated or the neighbourhood function is not mentioned._
- **P4** (0.5): Shrink the neighbourhood radius and decay the learning rate, then loop: repeat sampling until ordering and convergence are complete, then stop. _Partial: Half if only the decay or only the loop/stopping condition is given._


## digiklausur/6 (2 marks)

**Question:** Give the basic idea of an SVM using the correct terminology!

**Model answer:** SVMs are linear learnable machines in the simplest case. It uses a decision boundary with maximum margin to classify the data into different classes. The data points which are near the decision boundary are called support vectors and the margin is determined based on these points. Kernels are used to separate non-linearly separable data and the algorithm is solved by using Quadratic Programming.

_Marking stance: moderate. Full marks need the maximum-margin decision boundary idea and the term support vectors (the points nearest the boundary that fix the margin). Kernels for non-linear data and quadratic programming are a valid alternative for the second point's detail, but are not both required. Give part marks for vague or incomplete wording; give none for wrong or unrelated answers, such as confusing SVMs with neural networks._

- **P1** (1): States that an SVM is a (linear) classifier that finds a decision boundary (hyperplane) with maximum margin to separate the classes. _Partial: Half if it mentions a decision boundary/separating line but not the maximum margin (or margin without the boundary)._
- **P2** (1): States that the data points closest to the decision boundary are the support vectors and that they determine the margin; and/or that kernels are used for non-linearly separable data (optionally solved with quadratic programming). _Partial: Half if support vectors are named without linking them to the margin or being the nearest points, or if only kernels/quadratic programming are mentioned._


## digiklausur/7 (2 marks)

**Question:** What role does the method of steepest decent have when learning a network?

**Model answer:** Steepest descent is used to update the weights in a NN during the learning phase. It helps to navigate the cost function and find the parameters for which the cost is minimum. The weights are updated in the direction of the steepest descent which is in a direction opposite to the gradient vector. This method could suffer from local minima and may become unstable.

_Marking stance: moderate. Full marks need the role (updating weights to minimise the cost function) and the mechanism (step opposite to the gradient vector). Give half for a vague or incomplete version of either idea. Mentioning local minima or instability is optional and not required for marks. Give no marks for wrong or off-topic answers._

- **P1** (1): States that steepest (gradient) descent is used to update the weights/parameters of the network during learning/training, in order to minimise the cost (error) function. _Partial: Half if only says it is used for learning/optimisation, or only mentions updating weights or minimising cost, without linking both._
- **P2** (1): States that weights are changed in the direction of steepest descent, i.e. opposite to the gradient vector of the cost function. _Partial: Half if mentions the gradient or moving downhill but does not clearly say the update is opposite to the gradient._


## digiklausur/8 (2 marks)

**Question:** Define: a hypothesis $h \in H$ shatters a dataset $A \subseteq X \Leftrightarrow \ldots$

**Model answer:** For all 2^N possible binary labeling of every data, if a hypothesis h splits the positive data from the negative data with no error, then it means that the hypothesis h shatters the dataset A.

_Marking stance: moderate. Full marks need both ideas: every one of the 2^N binary labelings, and h separates positives from negatives with zero error. Give part marks when one idea is vague or incomplete (e.g. 'h can separate the data' with no mention of all labelings). Give no marks for answers that describe something else, such as a single labeling only or VC dimension without the definition. Wording may differ; an equivalent formal statement is fine._

- **P1** (1): States that the hypothesis h must handle every possible labeling of the dataset A: for all 2^N possible binary (positive/negative) labelings of the N data points. _Partial: Half if it mentions labelings/assignments of positive and negative but omits 'all' or 2^N, or is vague about covering every labeling._
- **P2** (1): States that for each such labeling, h separates the positive from the negative points with no error (classifies all points correctly); hence h shatters A. _Partial: Half if it says h separates/classifies the data but does not say without error, or implies it only for some labelings._


## digiklausur/9 (2 marks)

**Question:** Write down and explain the Widrow-Hoff learning rule!

**Model answer:** The adjustment made to a synaptic weight of a neuron is proportional to the product of the error signal and the input signal of the synapse in question. The rule is derived from the steepest descent method.

_Marking stance: moderate. Full marks: the weight change is proportional to error times the synapse's input, and the rule comes from steepest (gradient) descent. Give half for each idea that is vague or incomplete, such as naming only error or only input, or saying only that it minimises error. No marks for a different rule (e.g. Hebbian or perceptron rule) or unrelated content._

- **P1** (1): States the rule: the weight adjustment (change in synaptic weight) is proportional to the product of the error signal and the input signal of that synapse (e.g. Δw_kj = η e_k x_j, with learning rate η). _Partial: Half if only one of error or input is mentioned, or proportionality/product is stated vaguely without clear terms._
- **P2** (1): Explains that the rule is derived from / is based on the steepest (gradient) descent method, i.e. minimising the error (cost) by moving weights against the gradient. _Partial: Half if it only says the rule reduces/minimises error without naming steepest or gradient descent._
