"""
Test script for Publisher PDF generation.

Tests the complete PDF publishing workflow including cover page generation,
markdown-to-PDF conversion, and PDF merging. Uses comprehensive sample data
to generate a 7-8 page test report.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from publisher.publisher import Publisher


SAMPLE_TABLE_OF_CONTENTS = """
## 1. Introduction to Neural Networks
   - 1.1 Historical Background
   - 1.2 Basic Concepts and Terminology
   - 1.3 Biological Inspiration

## 2. Architecture of Neural Networks
   - 2.1 Neurons and Activation Functions
   - 2.2 Layers and Network Topologies
   - 2.3 Feedforward vs Recurrent Networks

## 3. Mathematical Foundations
   - 3.1 Linear Algebra Fundamentals
   - 3.2 Gradient Descent Optimization
   - 3.3 Backpropagation Algorithm

## 4. Training and Optimization
   - 4.1 Loss Functions
   - 4.2 Regularization Techniques
   - 4.3 Hyperparameter Tuning

## 5. Applications and Use Cases
   - 5.1 Computer Vision
   - 5.2 Natural Language Processing
   - 5.3 Reinforcement Learning

## 6. Conclusion and Future Directions
"""

SAMPLE_ABSTRACT = """
This comprehensive research report explores the fundamental principles and mechanisms of neural networks, providing an in-depth analysis of their architecture, mathematical foundations, and practical applications. Neural networks have revolutionized machine learning and artificial intelligence, enabling breakthrough achievements in computer vision, natural language processing, and autonomous decision-making systems.

The research synthesizes current literature and experimental findings to present a holistic view of how neural networks learn from data through iterative optimization processes. We examine the biological inspiration behind artificial neurons, trace the historical development of key architectures, and provide detailed mathematical derivations of core algorithms including gradient descent and backpropagation.

Key findings indicate that the success of modern neural networks stems from three critical factors: increased computational power, availability of large-scale datasets, and architectural innovations such as convolutional and attention-based mechanisms. The report concludes with an analysis of current limitations and emerging research directions that promise to further advance the field.
"""

SAMPLE_INTRODUCTION = """
Neural networks represent one of the most significant technological advances of the 21st century, fundamentally transforming how machines learn from and interact with data. Originally inspired by biological neural systems, these computational models have evolved into sophisticated architectures capable of solving complex problems that were previously considered intractable.

### Historical Context

The concept of artificial neural networks dates back to the 1940s when Warren McCulloch and Walter Pitts proposed the first mathematical model of a neuron. This pioneering work laid the foundation for decades of research, though progress was initially slow due to computational limitations and theoretical challenges.

The field experienced several "winters" where funding and interest waned, only to resurge with renewed vigor. The 2010s marked a renaissance period, driven by:

- **Increased computational power**: GPUs enabled parallel processing of neural network operations
- **Big data availability**: Internet-scale datasets provided the training material needed for deep learning
- **Algorithmic innovations**: New architectures like ResNets and Transformers overcame previous limitations

### Research Objectives

This report aims to provide a comprehensive understanding of neural networks by:

1. Explaining the fundamental building blocks and their mathematical representations
2. Analyzing the training process and optimization techniques
3. Surveying real-world applications across multiple domains
4. Identifying current limitations and future research directions

The intended audience includes researchers, practitioners, and students seeking a thorough grounding in neural network theory and practice.
"""

SAMPLE_BODY = """
# Chapter 1: Architecture of Neural Networks

## 1.1 Neurons and Activation Functions

At the heart of every neural network lies the artificial neuron, a computational unit that transforms input signals into output signals through a non-linear function. The mathematical model of a neuron can be expressed as:

$$y = f(\\sum_{i=1}^{n} w_i x_i + b)$$

Where:
- $x_i$ represents input values
- $w_i$ represents weight parameters
- $b$ represents the bias term
- $f$ is the activation function

### Common Activation Functions

| Function | Formula | Range | Use Cases |
|----------|---------|-------|-----------|
| Sigmoid | $\\sigma(x) = 1/(1+e^{-x})$ | (0, 1) | Binary classification, gates |
| Tanh | $\\tanh(x) = (e^x - e^{-x})/(e^x + e^{-x})$ | (-1, 1) | Hidden layers, RNNs |
| ReLU | $f(x) = \\max(0, x)$ | [0, ∞) | Deep networks, CNNs |
| Softmax | $\\sigma(x)_j = e^{x_j}/\\sum_k e^{x_k}$ | (0, 1) | Multi-class output |

The choice of activation function significantly impacts network performance. ReLU has become the default choice for deep networks due to its computational efficiency and ability to mitigate the vanishing gradient problem.

## 1.2 Layers and Network Topologies

Neural networks are organized into layers, with each layer performing specific transformations on the data:

**Input Layer**: Receives raw data and passes it to the network. No computation occurs here; it simply serves as the entry point for features.

**Hidden Layers**: Process information through weighted connections and activation functions. The term "deep learning" refers to networks with multiple hidden layers.

**Output Layer**: Produces the final prediction or classification. The structure depends on the task:
- Single neuron with sigmoid for binary classification
- Multiple neurons with softmax for multi-class problems
- Linear neurons for regression tasks

### Network Width vs Depth

Research has shown that deeper networks can represent more complex functions with fewer parameters than wider, shallow networks. This efficiency comes from the hierarchical feature learning capability of deep architectures.

```
Input → [Hidden 1: 64 units] → [Hidden 2: 128 units] → [Hidden 3: 64 units] → Output
```

The universal approximation theorem states that a sufficiently wide single-layer network can approximate any continuous function. However, deep networks achieve the same with exponentially fewer neurons.

---

# Chapter 2: Mathematical Foundations

## 2.1 Linear Algebra Fundamentals

Neural network operations are fundamentally matrix transformations. Understanding linear algebra is essential for grasping how networks process data.

### Vector and Matrix Operations

For a layer with input vector $\\mathbf{x} \\in \\mathbb{R}^n$ and weight matrix $\\mathbf{W} \\in \\mathbb{R}^{m \\times n}$:

$$\\mathbf{z} = \\mathbf{W}\\mathbf{x} + \\mathbf{b}$$

This operation is computed efficiently using GPU parallelization, enabling the training of networks with millions of parameters.

### Tensor Representations

Modern deep learning frameworks use tensors—multi-dimensional arrays—for data representation:

| Dimension | Use Case | Example Shape |
|-----------|----------|---------------|
| 0D (Scalar) | Loss value | () |
| 1D (Vector) | Bias terms | (128,) |
| 2D (Matrix) | Weight matrix | (256, 128) |
| 3D (Tensor) | Batch of sequences | (32, 100, 512) |
| 4D (Tensor) | Batch of images | (32, 224, 224, 3) |

## 2.2 Gradient Descent Optimization

Gradient descent is the cornerstone optimization algorithm for training neural networks. The algorithm iteratively adjusts parameters to minimize a loss function:

$$\\theta_{t+1} = \\theta_t - \\eta \\nabla L(\\theta_t)$$

Where:
- $\\theta$ represents all learnable parameters
- $\\eta$ is the learning rate
- $\\nabla L$ is the gradient of the loss function

### Variants of Gradient Descent

**Batch Gradient Descent**: Computes gradients over the entire dataset. Provides accurate gradient estimates but is computationally expensive for large datasets.

**Stochastic Gradient Descent (SGD)**: Updates parameters after each sample. Introduces noise that can help escape local minima but leads to unstable convergence.

**Mini-batch Gradient Descent**: Balances the trade-offs by computing gradients over small batches. This is the standard approach in modern deep learning.

### Advanced Optimizers

Modern optimizers incorporate adaptive learning rates and momentum:

- **Adam**: Combines momentum with adaptive learning rates per parameter
- **RMSprop**: Adapts learning rates based on recent gradient magnitudes
- **AdaGrad**: Accumulates squared gradients for adaptive learning rates

## 2.3 Backpropagation Algorithm

Backpropagation enables efficient computation of gradients through the chain rule of calculus. For a composite function $L(f(g(x)))$:

$$\\frac{\\partial L}{\\partial x} = \\frac{\\partial L}{\\partial f} \\cdot \\frac{\\partial f}{\\partial g} \\cdot \\frac{\\partial g}{\\partial x}$$

The algorithm proceeds in two phases:

1. **Forward Pass**: Compute activations layer by layer, storing intermediate values
2. **Backward Pass**: Compute gradients from output to input, applying the chain rule

This computational efficiency—O(n) where n is the number of parameters—enables training of very deep networks.

---

# Chapter 3: Training and Optimization

## 3.1 Loss Functions

The choice of loss function defines what the network optimizes during training:

### Classification Losses

**Cross-Entropy Loss**: Measures the divergence between predicted probabilities and true labels:

$$L = -\\sum_{c=1}^{C} y_c \\log(\\hat{y}_c)$$

This is the standard loss for classification tasks, penalizing confident wrong predictions more heavily.

**Hinge Loss**: Used in SVMs and some neural network applications:

$$L = \\max(0, 1 - y \\cdot \\hat{y})$$

### Regression Losses

| Loss Function | Formula | Characteristics |
|---------------|---------|-----------------|
| MSE | $\\frac{1}{n}\\sum(y - \\hat{y})^2$ | Penalizes large errors heavily |
| MAE | $\\frac{1}{n}\\sum|y - \\hat{y}|$ | Robust to outliers |
| Huber | Combination of MSE and MAE | Best of both approaches |

## 3.2 Regularization Techniques

Regularization prevents overfitting by constraining the model complexity:

**L2 Regularization (Weight Decay)**: Adds squared magnitude of weights to the loss:

$$L_{total} = L_{task} + \\lambda \\sum_i w_i^2$$

**Dropout**: Randomly sets activations to zero during training:

> "Dropout provides an efficient way of combining exponentially many different neural network architectures." - Srivastava et al., 2014

The technique forces the network to learn redundant representations that generalize better.

**Batch Normalization**: Normalizes layer inputs to have zero mean and unit variance:

$$\\hat{x} = \\frac{x - \\mu}{\\sqrt{\\sigma^2 + \\epsilon}}$$

This stabilizes training and allows higher learning rates.

## 3.3 Hyperparameter Tuning

Key hyperparameters that affect training:

1. **Learning Rate**: Too high causes divergence; too low causes slow convergence
2. **Batch Size**: Larger batches provide stable gradients but may generalize poorly
3. **Network Architecture**: Number of layers, neurons per layer, connection patterns
4. **Regularization Strength**: Balance between fitting training data and generalization

### Tuning Strategies

- **Grid Search**: Exhaustive search over a predefined grid of values
- **Random Search**: Sample hyperparameters from distributions
- **Bayesian Optimization**: Model the objective function and select promising points
- **Learning Rate Schedules**: Decay learning rate during training

---

# Chapter 4: Applications and Use Cases

## 4.1 Computer Vision

Convolutional Neural Networks (CNNs) have transformed computer vision:

**Image Classification**: Networks like ResNet achieve superhuman accuracy on ImageNet, correctly classifying objects among 1000 categories.

**Object Detection**: Modern detectors like YOLO and Faster R-CNN localize and classify multiple objects in real-time applications.

**Semantic Segmentation**: Pixel-wise classification enables autonomous driving, medical imaging, and satellite imagery analysis.

### Key Architectural Components

| Component | Purpose | Innovation |
|-----------|---------|------------|
| Convolution | Local feature extraction | Weight sharing, translation invariance |
| Pooling | Spatial downsampling | Invariance to small transformations |
| Skip Connections | Gradient flow in deep networks | Enables training of 100+ layer networks |
| Attention | Global context modeling | Focus on relevant image regions |

## 4.2 Natural Language Processing

Transformer architectures have revolutionized NLP:

**Language Models**: GPT and BERT variants understand and generate human-like text, enabling:
- Text summarization
- Question answering
- Sentiment analysis
- Machine translation

**Key Innovations**:
- **Self-Attention**: Models relationships between all tokens in a sequence
- **Pre-training**: Learn from vast unlabeled text corpora
- **Fine-tuning**: Adapt to specific tasks with limited labeled data

## 4.3 Reinforcement Learning

Neural networks serve as function approximators in RL:

**Deep Q-Networks (DQN)**: Achieved human-level performance on Atari games by combining Q-learning with CNN feature extraction.

**Policy Gradient Methods**: Directly optimize the policy function, enabling continuous action spaces in robotics.

**AlphaGo and AlphaZero**: Combined deep learning with Monte Carlo Tree Search to master the game of Go and other board games.
"""

SAMPLE_CONCLUSION = """
# Conclusion

## Summary of Findings

This comprehensive analysis of neural networks has revealed the sophisticated interplay between biological inspiration, mathematical foundations, and engineering innovations that enable modern deep learning systems. Key insights include:

1. **Architectural Flexibility**: Neural networks can be configured for diverse tasks through appropriate choice of layers, activations, and connection patterns.

2. **Mathematical Rigor**: The backpropagation algorithm, combined with gradient-based optimization, provides an efficient framework for learning from data.

3. **Practical Impact**: Applications span computer vision, natural language processing, robotics, and scientific discovery.

## Current Limitations

Despite remarkable progress, significant challenges remain:

- **Data Dependency**: Deep networks require large labeled datasets, limiting applications in data-scarce domains
- **Interpretability**: "Black box" nature hinders adoption in high-stakes applications
- **Computational Cost**: Training large models requires substantial energy and hardware resources
- **Adversarial Vulnerability**: Small input perturbations can cause catastrophic failures

## Future Directions

Emerging research areas promise to address these limitations:

> "The future of AI lies not in bigger models, but in smarter architectures and learning algorithms that can do more with less."

**Promising Trends**:
- Few-shot and zero-shot learning for data efficiency
- Neuro-symbolic AI for interpretability
- Efficient architectures for edge deployment
- Robust training methods for adversarial resilience

## Recommendations

For practitioners and researchers entering the field:

1. Build strong foundations in linear algebra, calculus, and probability theory
2. Gain hands-on experience with modern frameworks (PyTorch, TensorFlow)
3. Study seminal papers and their architectural innovations
4. Focus on problem-specific data preprocessing and augmentation
5. Consider ethical implications and societal impact of AI systems

The neural network revolution continues to accelerate, promising transformative applications across virtually every domain of human endeavor.
"""


SAMPLE_STATE = {
    'user_query': 'How Neural Networks Work: Architecture, Mathematics, and Applications',
    'report_table_of_contents': SAMPLE_TABLE_OF_CONTENTS,
    'report_abstract': SAMPLE_ABSTRACT,
    'report_introduction': SAMPLE_INTRODUCTION,
    'report_body': SAMPLE_BODY,
    'report_conclusion': SAMPLE_CONCLUSION,
    'planner_query': [
        {'query_num': 1, 'query': 'Neural network architecture and components'},
        {'query_num': 2, 'query': 'Mathematical foundations of deep learning'},
        {'query_num': 3, 'query': 'Training and optimization techniques'},
        {'query_num': 4, 'query': 'Applications in computer vision and NLP'},
    ]
}


async def run_publisher_test():
    """
    Executes complete PDF publishing test.
    
    Generates a 7-8 page PDF report from sample state data including
    table of contents, abstract, introduction, body chapters, and
    conclusion. Prints the output path on success.
    """
    print("=" * 60)
    print("PUBLISHER PDF GENERATION TEST")
    print("=" * 60)
    
    publisher = Publisher()
    
    print("\n[1/3] Creating report layout...")
    layout = publisher._create_report_layout(SAMPLE_STATE)
    print(f"   Layout created: {len(layout)} characters")
    
    print("\n[2/3] Generating PDF with cover page...")
    result = await publisher.run('pdf', SAMPLE_STATE.copy())
    
    print("\n[3/3] Result:")
    final_path = result.get('final_report_path', 'Failed')
    
    if final_path and final_path != 'Failed':
        print(f"   ✅ PDF generated successfully!")
        print(f"   📄 Path: {final_path}")
        
        if os.path.exists(final_path):
            size_kb = os.path.getsize(final_path) / 1024
            print(f"   📊 Size: {size_kb:.1f} KB")
    else:
        print("   ❌ PDF generation failed")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(run_publisher_test())
