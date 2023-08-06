# expsweep - Experiment Sweeper

Easily run Monte Carlo experiments on a function by sweeping parameters and running multiple repetitions.
Results are returned in a Pandas dataframe that can easily be plotted.

## Features

- automatically parallelizes experiment
- results are returned as a Pandas table which can be easily plotted in seaborn

## Quickstart

    pip install expsweep

Basic Example - two simultaneous experiments with a single variable sweep

``` python
import expsweep

# Function to run Monte Carlo experiment on.
# Should return a dictionary containing experiment results.
def exp(x):
    return {
        'experiment1': np.random.normal(loc=x, scale=x),
        'experiment2': np.random.normal(loc=3 * x, scale=x)
    }
    

# Run Monte Carlo experiment on exp() function.
# Sweep parameter x (with 20 repetitions for each x) and collect results.
# Parallelize with 32 cores
mc = expsweep.experiment(
    exp,
    repeat=20,
    x=range(10),
    cpu_count=32,
)

"""
>>> mc
     x  experiment1  experiment2
0    0     0.000000     0.000000
1    0     0.000000     0.000000
2    0     0.000000     0.000000
..  ..          ...          ...
197  9    14.120838    27.557313
198  9    11.443396    21.961869
199  9    14.120838    27.557313
"""
```

Plotting with Seaborn

``` python
# Seaborn expects data from both experiments to be in one column.
# Use `merge=True` to merge experiment columns together for Seaborn.
mc = expsweep.experiment(
    exp,
    repeat=20,
    x=range(10),
    cpu_count=32,
    merge=True
)

"""
>>> mc
     x   experiment     result
0    0  experiment1   0.000000
1    0  experiment1   0.000000
2    0  experiment1   0.000000
..  ..          ...        ...
397  9  experiment2  17.528782
398  9  experiment2  17.528782
399  9  experiment2  27.557313
"""

import seaborn as sns
sns.lineplot(
    data=mc,
    x='x',
    y='result',
    hue='experiment',
    style='experiment',
)
```

![](example_plot.png)

## Multiple Parameters and Fixed Parameters

More parameters can be swept combinatorially by simply providing more arguments:

```python

def exp(x, y, z):
    ...
    return {'experiment1': ...}
    
mc = expsweep.experiment(
    exp,
    x=range(10),
    y=range(10),
    z=[1]
)

>>> mc
     x  y  z  experiment1
0    0  0  1     0.000000
1    1  0  1     0.000000
2    2  0  1     0.000000
..  ..  .             ...
97   7  9  1    17.528782
98   8  9  1    17.528782
99   9  9  1    27.557313
"""
```

## Other Arguments

#### def experiment(...)
               
- **func** (function) - function to run Monte Carlo simulation on
- **disable_print** (boolean) - whether to show progress bars. (default False)
- **repeat** (int) - number of repetitions for each parameter combination. (default 1)
- **merge** (bool) - merge all experiment results into single data column ("results") and create new categorical column ("experiment").  (default False)
- **cpu_count** (int) - number of jobs to create.  If None, use all available cpus.  (default None)
- **backend** (str) - use pqdms "processes" backend or "threads" backend ([more info](https://pqdm.readthedocs.io/en/latest/usage.html)). (default "processes")
- **pqdm_kwargs** (dict) - arguments to pass to pqdm (default None)

## Troubleshooting

    AttributeError: Can't pickle local object ...
    
Define the variable in question as a global or switch the backend to 'threads'.

