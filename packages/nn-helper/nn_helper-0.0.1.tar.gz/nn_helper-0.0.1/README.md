<div id="top"></div>

# nn-helper

<!-- ABOUT THE PROJECT -->
## About The Project

This project is a wrapper for Pytorch neural networks (NNs) to obfuscate functionalities that are always used during training and testing of NNs. Such as loggers, training loops, and saving of NNs.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

These are the libraries and frameworks with which the library is constructed:

* [Python](https://python.org/)
* [Pytorch](https://pytorch.org/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started Locally

This section explains how to set-up the repository locally from this repository. Note that this explanation is compatible for a MacOS / Linux environment.

### Prerequisites

1. Have at least Python 3.8 installed on your local machine.
2. Make sure to have [make](https://www.gnu.org/software/make/) installed. Else, you can copy paste commands from the Makefile into your terminal.

### Installation

1. Clone the repo and cd into it
   ```sh
   git clone https://gitlab.com/markdeblaauw/nn-helper.git
   ```
3. Create a Python virtual environment
    ```sh
    make virtual_env
    . venv/bin/activate
    ```
4. Install the development Python package
    ```sh
    make install_dev_package
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage
You can find the following example of using the library in the `examples` folder:

```python
import math

import models.linear_regression as linear_model
import torch

import nn_helper
from nn_helper.callbacks.verbose_logger import VerboseLogger


def run_model():
    # Create Tensors to hold input and outputs.
    x = torch.linspace(-math.pi, math.pi, 2000)
    y = torch.sin(x)

    p = torch.tensor([1, 2, 3])
    xx = x.unsqueeze(-1).pow(p)

    # Only 1 sample. Hence, batch size of 1.
    data_loader = torch.utils.data.DataLoader(dataset=linear_model.Dataset(x=xx, y=y), batch_size=1)

    loss_fn = torch.nn.MSELoss()

    model = linear_model.LinearRegression()

    optimizer = torch.optim.Adam(params=model.parameters(), lr=1e-2)

    # Train the model with 10 epochs and use
    # Verbose Logger to put metrics to terminal.
    nn_helper.fit(
        model=model,
        data_loader=data_loader,
        epochs=10,
        loss_fn=loss_fn,
        optimizer=optimizer,
        callbacks=[VerboseLogger()],
    )
```

### Testing

You can run unit tests locally as follows:
```bash
make tests
```

A coverage report can be generated with the intention of 100% coverage:
```bash
make coverage_report
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Roadmap

The library is not complete yet. Certain features, such as metric computation, testing and many callbacks, are not implemented yet. These will be implemented in due time.

<p align="right">(<a href="#top">back to top</a>)</p>