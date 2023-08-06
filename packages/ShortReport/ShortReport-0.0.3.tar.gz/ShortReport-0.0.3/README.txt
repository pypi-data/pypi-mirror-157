# ShortReport



This library is used to generate a `report`. Features in this library are:

- **Numbers and Types**: Shows the number of columns and rows present in the dataset. Also describe the type of columns.
- **Essentials**: Unique values in a column and Numbers of missing values
- **Descriptive statistics**: Mean and Standard Deviation.
- **Graphs**: Short Report includes different plotly graphs for better visualization like Histograms for data distribution of each column, Scatter Plot for finding the relationships or pattern between the attributes or columns, Heat Map for finding the correlation with target variable and Boxplot for outlier detection.
- **Data Summary**: includes Numbers of zeros and percentage, Maximum and Minimum value.

### Advantages:
- ***User Friendly***: This Library helps user to understand the nature of data easily in very efficient way.
- ***Graphs***: All graphs are made from plotly so user can interact with the graph values.
- ***Fast***: Generates report in milliseconds.
- ***Info***: Gives the basic info which


## Quickstart

Import ShortReport and create a Dataframe

```python
from ShortReport import Report as r
import pandas as pd
import numpy as np
df = pd.DataFrame(np.random.rand(100,4), columns = ['X','Y','Z','A'])
```
Call the method shortreport and it requires one argument which should be a Dataframe
```python
r.shortreport(df)
```
## Output on Jupyter Notebook

Dataset_report:

<img alt="HTML" src="https://i.imgur.com/AVfsypQ.gif" width="800" />

Correlation:

![Correlation](https://i.imgur.com/9LevkVH_d.webp?maxwidth=760&fidelity=grand)
## Installation

### Using pip

```sh
pip install ShortReport
```

### Using conda
 
```sh
conda install ShortReport
```