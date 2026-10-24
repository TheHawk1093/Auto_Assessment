# digiklausur: sized rubrics

Marks per point add up to the question total.

## digiklausur/10 (2 marks)

**Question:** Explain back propagation, use the correct technical terms!

**Model answer:** Backpropagation lowers the error of a MLP level by level recursively backwards. It back propagates an error from the last layer to the first layer by updating the weights. The updates are determined by the local gradient at each level which is computed by partial derivatives of the error and chain rule.

- **P1** (1): States that backpropagation reduces/minimises the error (loss) of a multi-layer network (MLP) by propagating the error backwards from the output (last) layer to the first layer, layer by layer (recursively), updating the weights. Equivalent wording accepted.
- **P2** (1): States that the weight updates are determined by the local gradient at each layer, computed using partial derivatives of the error with respect to the weights and the chain rule (gradient descent). _Partial: Half credit if only one of gradient/partial derivatives or chain rule is mentioned._


## digiklausur/11 (2 marks)

**Question:** When learning using steepest descent, explain the role of the learning rate? What is a danger?

**Model answer:** Learning rate controls the speed of the convergence. When the learning rate is low, the convergence is overdamped and slow. When the learning rate is high, the convergence is underdamped and follows a zigzagging path. When the learning rate exceeds a critical value learning becomes unstable.

- **P1** (1): States that the learning rate controls the speed of convergence (low rate gives slow/overdamped convergence; high rate gives faster but zigzagging/underdamped convergence). Equivalent wording accepted.
- **P2** (1): States the danger: if the learning rate exceeds a critical (maximum) value, learning becomes unstable (diverges).


## digiklausur/14 (2 marks)

**Question:** Describe: the structure on an CNN.

**Model answer:** Convolutional Neural Network consists of many layers such as a convolutional layer that has kernels which convolve over the input image, an activation layer (ReLU activation), pooling layer (max or average pooling), and one or more fully connected layers followed by softmax layer.

- **P1** (1): Names the convolutional layer (kernels/filters convolving over the input image) together with an activation layer (e.g. ReLU) as the feature-extraction part of the network. Equivalent wording accepted. _Partial: Half if only the convolutional layer or only the activation layer is given._
- **P2** (1): Names a pooling layer (max or average pooling) and one or more fully connected layers followed by a softmax (output) layer. Equivalent wording accepted. _Partial: Half if only the pooling layer or only the fully connected/softmax part is given._


## digiklausur/16 (2 marks)

**Question:** Describe how learning based on k-nearest neighbors works, use pseudo code!

**Model answer:** Add the new data to the members of colored or classified old data, construct a sphere with k nearest data points, find the class or color which has the maximum vote and assign the new data to the class which has the maximum vote in an unsupervised manner.

- **P1** (1): Describes the setup/first step: new data point is compared with the existing labelled (classified) data, and the k nearest data points (neighbours, by distance) to the new point are identified/selected.
- **P2** (1): Takes a majority vote among the k nearest neighbours' classes and assigns the new data point to the class with the maximum vote. Equivalent wording accepted. Pseudo code or clear step-by-step algorithm form is acceptable.


## digiklausur/3 (2 marks)

**Question:** Assume you want to binary classify linear separable data point using a perceptron. Write down the learning algorithm in pseudo code!

**Model answer:** Label the data with positive and negative (+/-) labels, initialize the weights randomly, apply (simplified) update rule: Dw = eta*x(n) if <w,x> <= 0, repeat on all epochs till the weights don’t change much. The algorithm will converge as the data is linearly separable.

- **P1** (1): Setup: labels the data as positive/negative (e.g. +1/−1) and initializes the weights (randomly or otherwise).
- **P2** (1): Loop/update: repeatedly goes over the data (epochs); for a misclassified point (e.g. <w,x> <= 0 after sign-adjusting by label, or y·<w,x> <= 0) updates w by adding eta*x (or eta*y*x); stops when weights no longer change / no misclassifications (converges since data is linearly separable). Equivalent wording and equivalent update formulations earn the marks.


## digiklausur/4 (2 marks)

**Question:** Explain classification and regression; what is the difference?

**Model answer:** Classification is a task of mapping data to discrete labels while regression is a task which maps data to a continuous function or real values. Error in classification is the number of misclassifications while in regression is the summed distance between the true and predicted values.

- **P1** (1): Defines classification as mapping data/inputs to discrete labels (categories/classes) and regression as mapping data to continuous values (real-valued outputs/function). Equivalent wording accepted. _Partial: Half if only one of classification or regression is correctly defined._
- **P2** (1): States how error differs: classification error is the number (count) of misclassifications, whereas regression error is the summed distance/difference between true and predicted values. Equivalent wording accepted. _Partial: Half if only one of the two error measures is correctly stated._


## digiklausur/5 (2 marks)

**Question:** Write down the SOM learning in pseudo code.

**Model answer:** Arrange the weights in the required topology according to the problem. Initialize the weights randomly such that all the weights are different. Sample the input from the input space. Similarity matching: match the input to a neuron in the topological lattice which becomes the winning neuron. Update the weights of the winning neuron and its neighbours determined by the neighbourhood function. Reduce the neighbourhood and decay the learning rate and share radius. If ordering and convergence are complete, stop. Else continue sampling from the input space.

- **P1** (0.5): Initialisation: arranges weights in the required lattice/topology and initialises them randomly (all different); then samples an input vector from the input space (equivalent wording accepted).
- **P2** (0.5): Similarity matching: finds the winning neuron/best matching unit for the input in the lattice (e.g. minimum distance).
- **P3** (0.5): Updates weights of the winning neuron and its neighbours using the neighbourhood function (and learning rate).
- **P4** (0.5): Reduces neighbourhood radius and decays learning rate; loops back to sampling until ordering/convergence is complete, then stops.


## digiklausur/6 (2 marks)

**Question:** Give the basic idea of an SVM using the correct terminology!

**Model answer:** SVMs are linear learnable machines in the simplest case. It uses a decision boundary with maximum margin to classify the data into different classes. The data points which are near the decision boundary are called support vectors and the margin is determined based on these points. Kernels are used to separate non-linearly separable data and the algorithm is solved by using Quadratic Programming.

- **P1** (1): States that an SVM is a (linear) classifier that finds a decision boundary (hyperplane) with maximum margin to separate the classes.
- **P2** (1): Names support vectors as the data points closest to the decision boundary, which determine the margin. Mentioning kernels for non-linearly separable data and/or quadratic programming is a fine addition but not required.
