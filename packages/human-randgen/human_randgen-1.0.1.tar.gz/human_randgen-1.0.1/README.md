# Human Random Generator

This is a simple package which makes it easy to generate random numbers with a distribution following human response times. It is possible to fine-tune the generator with existing data (e.g., time between mouse clicks).

## Installation

```pip install human_randgen```

## Usage

Initialize the generator with your choice of mode and standard deviation. These parameters depend on your use case. For example, if you are simulating a person clicking a mouse every 2 +- 1 seconds, you could try:

```
from human_randgen.model import HumanRng

rng = HumanRng(mode=2, sigma=1)
```

Generate random numbers using the `rand(num_samples=1)` function:
```
rng.rand()
```

Finally, update the generator with existing data with the `fit` function:
```
rng.fit([2.2, 1.8, 5.4, 2.1])
```

This is useful if you are not sure what the mode and standard deviation should be during initialization.

Calling the `fit` function will update the mode and standard deviation based on the data, and all following calls to `rand` will use the updated parameters. In addition, the updated values will be printed out to console. You can save them to reinitialize the generator with the fitted parameters from the onset.

The `fit` function can be called as many times as you want. The more data you pass to this function, the less influence your choice of initialization parameters will have.

## Internals
The underlying distribution is lognormal, which is said to represent many human behaviors. During initialization, Newton's method is used to calculate the mean and variance of the lognormal distribution from the given parameters.

For fitting, we add a normal-inverse-gamma distribution as the conjugate prior on the parameters and perform MAP estimation.
