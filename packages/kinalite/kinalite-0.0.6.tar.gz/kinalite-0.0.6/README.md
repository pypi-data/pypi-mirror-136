Kinalite - Simple VTNA
======================

Kinalite is a Python package that provides a simple API for running Variable Time Normalization
Analysis on chemical data.

### Requirements

Python 3.6+

### Installation

Kinalite can be installed with pip:

    $ pip install kinalite
        
Usage
-----

To use kinalite you will need to provide two DataFrames with experiment data to compare. Kinalite 
will then use VTNA to find a best order for the first experiment.

### Reading data

The first step is using the Pandas package to convert your experiment data into DataFrames:

```python
import pandas as pd

# supply an absolute or relative path to CSV files
experiment_a_data = pd.read_csv('./data/experiment_a.csv')
experiment_b_data = pd.read_csv('./data/experiment_b.csv')
```

These CSV files need to have a single header row and time in the first columns. All values, including 
Time, are numbers. For example:

|Time|C|A|B|D|cat|
|---|---|---|---|---|---|
|0|0|1|1|0|0.01|
|5|5.45911E-05|0.997274|0.997328|0.00267175|0.00994541|
|10|5.45909E-05|0.994555|0.99461|0.0053903|0.00994541|
|15|5.45907E-05|0.991844|0.991899|0.00810143|0.00994541|
|20|5.45906E-05|0.98914|0.989195|0.0108052|0.00994541|

### Running VTNA

Next you can use your converted data to create an `Experiment` and run VTNA. You must also provide the
column indexes for the substrate and product, starting at 0 (Time is column index 0):

```python
import pandas as pd
from kinalite.experiment import Experiment

# supply an absolute or relative path to CSV files
experiment_a_data = pd.read_csv('./data/experiment_a.csv')
experiment_b_data = pd.read_csv('./data/experiment_b.csv')

# create an experiment and supply the column indexes for the substrate and product
experiment = Experiment('A', [experiment_a_data, experiment_b_data], substrate_index=2, product_index=4)
# run VTNA and print out the best order
result = experiment.calculate_best_result()
print('Order in A: ', result.order)
```

### Plotting data

Kinalite provides some plotting methods to help visualize the results of running VTNA:

```python
from kinalite.plots import plot_experiment_results

plot_experiment_results(experiment)
```

### Example Script

There is also an example script with a comparison of multiple sets of data: [kinalite_example/main.py](https://gitlab.com/heingroup/kinalite_example/-/blob/master/main.py)