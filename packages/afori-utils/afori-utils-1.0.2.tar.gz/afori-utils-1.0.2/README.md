# Afori Utils

This package contains an aggregation of tools used by Dor Miron.
Afori is my cat, and he contributed some changes now and then.

## Installation

Run the following to install:

```python 
pip install afori_utils
```

## Usage
```python
from afori_utils import pyplot_utils
from afori_utils import sync_utils
from afori_utils import debug_utils
```

####Easily combile plotting function to subplots
```python
import matplotlib.pyplot as plt
from afori_utils.pyplot_utils import plot_to_ax

def some_plotting_function(arg1, args2, ax=None):
    x = something(arg1, arg2)
    y = something_else(arg1, arg2)
    ax.plot(x, y)


def other_plotting_function(arg1, ax=None):
    x = something(arg1)
    y = something_else(arg1)
    ax.plot(x, y)

# Possibility 1
some_plotting_function(arg1, args2)

# Possibility 2
fig, ax_list = plt.subplots(2, 1)
some_plotting_function(ax=ax_list[0])
other_plotting_function(ax=ax_list[1])
plt.show()
```


