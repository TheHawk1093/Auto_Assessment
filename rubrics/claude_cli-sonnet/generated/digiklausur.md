# digiklausur: generated rubrics

Marks per point add up to the question total.

## digiklausur/10 (2 marks)

**Question:** Explain back propagation, use the correct technical terms!

**Model answer:** Backpropagation lowers the error of a MLP level by level recursively backwards. It back propagates an error from the last layer to the first layer by updating the weights. The updates are determined by the local gradient at each level which is computed by partial derivatives of the error and chain rule.

- **P1** (1): States that backpropagation reduces/minimises the error (loss) of a multi-layer perceptron/neural network by updating the weights, propagating the error from the output (last) layer backwards through the layers to the first layer (layer by layer/recursively). _Partial: Half if only one of: error lowered by weight updates, or error passed backwards layer by layer, is stated._
- **P2** (1): States that the weight updates are determined by the local gradient at each layer, computed using partial derivatives of the error with respect to the weights and the chain rule. _Partial: Half if only gradients/derivatives are mentioned without the chain rule (or chain rule without gradient/partial derivatives)._


## digiklausur/11 (2 marks)

**Question:** When learning using steepest descent, explain the role of the learning rate? What is a danger?

**Model answer:** Learning rate controls the speed of the convergence. When the learning rate is low, the convergence is overdamped and slow. When the learning rate is high, the convergence is underdamped and follows a zigzagging path. When the learning rate exceeds a critical value learning becomes unstable.

- **P1** (1): States that the learning rate controls the speed (step size) of convergence: low rate gives slow (overdamped) convergence; high rate gives faster but oscillating/zigzagging (underdamped) convergence. _Partial: Half marks if only says it controls speed/step size, without describing the low/high effects._
- **P2** (1): States the danger: if the learning rate exceeds a critical value, learning becomes unstable (diverges). _Partial: Half marks if mentions oscillation/zigzagging as a danger but not instability/divergence._


## digiklausur/14 (2 marks)

**Question:** Describe: the structure on an CNN.

**Model answer:** Convolutional Neural Network consists of many layers such as a convolutional layer that has kernels which convolve over the input image, an activation layer (ReLU activation), pooling layer (max or average pooling), and one or more fully connected layers followed by softmax layer.

- **P1** (0.75): Convolutional layer(s) with kernels/filters that convolve over the input image (to extract features), followed by an activation layer such as ReLU. _Partial: Half marks if only the convolutional layer or only the activation is mentioned._
- **P2** (0.5): Pooling layer (max or average pooling) to downsample the feature maps.
- **P3** (0.5): One or more fully connected layers.
- **P4** (0.25): Final softmax (output) layer producing class probabilities.


## digiklausur/16 (2 marks)

**Question:** Describe how learning based on k-nearest neighbors works, use pseudo code!

**Model answer:** Add the new data to the members of colored or classified old data, construct a sphere with k nearest data points, find the class or color which has the maximum vote and assign the new data to the class which has the maximum vote in an unsupervised manner.

- **P1** (1): Uses labelled/classified training data and, for a new data point, identifies its k nearest neighbours (e.g., by computing distances to the stored labelled points and selecting the k smallest). _Partial: Half marks if neighbours are mentioned but the use of distance/nearness or the value k is unclear._
- **P2** (1): Takes a majority vote of the classes among the k nearest neighbours and assigns the new data point to the class with the most votes. _Partial: Half marks if the class is assigned but the voting/majority step is not explicit._


## digiklausur/3 (2 marks)

**Question:** Assume you want to binary classify linear separable data point using a perceptron. Write down the learning algorithm in pseudo code!

**Model answer:** Label the data with positive and negative (+/-) labels, initialize the weights randomly, apply (simplified) update rule: Dw = eta*x(n) if <w,x> <= 0, repeat on all epochs till the weights don’t change much. The algorithm will converge as the data is linearly separable.

- **P1** (0.5): Setup: data labelled with two classes (+/- , e.g. +1/-1) and weights initialised (randomly or otherwise).
- **P2** (1): Update rule: for a misclassified point (e.g. <w,x> <= 0 after sign-adjusting by label, or y*<w,x> <= 0), update w = w + eta*y*x (simplified: Δw = eta*x). Equivalent correct forms accepted. _Partial: 0.5 if update is given but without the condition for misclassification, or condition given without correct update._
- **P3** (0.5): Loop over all data points/epochs repeatedly until no more misclassifications / weights stop changing (convergence guaranteed since data is linearly separable).


## digiklausur/4 (2 marks)

**Question:** Explain classification and regression; what is the difference?

**Model answer:** Classification is a task of mapping data to discrete labels while regression is a task which maps data to a continuous function or real values. Error in classification is the number of misclassifications while in regression is the summed distance between the true and predicted values.

- **P1** (0.5): Classification maps data/inputs to discrete labels (categories/classes).
- **P2** (0.5): Regression maps data/inputs to continuous values (real-valued outputs/function).
- **P3** (0.5): Error in classification is measured by the number (count) of misclassifications (misclassification rate).
- **P4** (0.5): Error in regression is measured by the summed distance/difference between true and predicted values (e.g. sum of absolute or squared errors).


## digiklausur/5 (2 marks)

**Question:** Write down the SOM learning in pseudo code.

**Model answer:** Arrange the weights in the required topology according to the problem. Initialize the weights randomly such that all the weights are different. Sample the input from the input space. Similarity matching: match the input to a neuron in the topological lattice which becomes the winning neuron. Update the weights of the winning neuron and its neighbours determined by the neighbourhood function. Reduce the neighbourhood and decay the learning rate and share radius. If ordering and convergence are complete, stop. Else continue sampling from the input space.

- **P1** (0.5): Initialisation: arrange the neurons/weights in the required lattice topology and initialise weights randomly so that all are different.
- **P2** (0.5): Sample an input vector from the input space and perform similarity matching to find the winning neuron in the lattice.
- **P3** (0.5): Update the weights of the winning neuron and its neighbours as determined by the neighbourhood function.
- **P4** (0.5): Reduce the neighbourhood size and decay the learning rate; repeat sampling until ordering and convergence are complete, then stop. _Partial: Half of the marks (0.25) if only the decay/shrinking or only the loop/stopping condition is given._


## digiklausur/6 (2 marks)

**Question:** Give the basic idea of an SVM using the correct terminology!

**Model answer:** SVMs are linear learnable machines in the simplest case. It uses a decision boundary with maximum margin to classify the data into different classes. The data points which are near the decision boundary are called support vectors and the margin is determined based on these points. Kernels are used to separate non-linearly separable data and the algorithm is solved by using Quadratic Programming.

- **P1** (0.75): States that an SVM is a linear classifier/learning machine that separates classes with a decision boundary (hyperplane) chosen to have maximum margin. _Partial: Half credit if only decision boundary/hyperplane is mentioned without maximum margin (or vice versa)._
- **P2** (0.75): States that the data points closest to the decision boundary are called support vectors and that they determine the margin/boundary. _Partial: Half credit if support vectors are named but their role in determining the margin is not stated._
- **P3** (0.5): Mentions kernels (kernel trick) for handling non-linearly separable data, and/or that training is solved as a quadratic programming (optimisation) problem. Equivalent wording accepted. _Partial: Half credit if only one of kernels or quadratic programming is given._
