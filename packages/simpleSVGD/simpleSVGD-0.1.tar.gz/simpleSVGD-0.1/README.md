# simpleSVGD

This package is a tiny SVGD algorithm specifically developed to operate on distributions found in [HMCLab](https://github.com/larsgeb/HMCLab).
## Stein Variational Gradient Descent (SVGD) 
SVGD is a general purpose variational inference algorithm that forms a natural counterpart of gradient descent for optimization. SVGD iteratively transports a set of particles to match with the target distribution, by applying a form of functional gradient descent that minimizes the KL divergence.

For more information, please visit the original implementers project website - [SVGD](http://www.cs.utexas.edu/~qlearning/project.html?p=vgd), or their publication Qiang Liu and Dilin Wang. [Stein Variational Gradient Descent (SVGD): A General Purpose Bayesian Inference Algorithm](http://arxiv.org/abs/1608.04471). NIPS, 2016.
