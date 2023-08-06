# flamingo
<img src="https://github.com/jsmckenzie/flamingo/blob/main/docs/image.jpg" alt="From Wikipedia" height="150" align="right" caption="Text left hanging">

#### Extract annotations from .ndpa files and map on to the .ndpi image for use in other applications

* * *

[![PyPI version](https://badge.fury.io/py/flamingo-histology.svg)](https://pypi.org/project/flamingo-histology/)


## Install
```Python
conda create --name ndpi python=3.10
conda activate ndpi

conda install -c conda-forge openslide
conda install -c conda-forge openslide-python # probably better than the command above

conda install numpy matplotlib jupyterlab

pip install flamingo-histology

```

## Example image
Example annotations (not corresponding to real regions) are provided in the `example` folder for files that can be downloaded from the following locations:
- [test3-FITC 2 (485).ndpi](https://downloads.openmicroscopy.org/images/Hamamatsu-NDPI/manuel/)


## Usage
```
import sys
from flamingo.Flamingo import HE


```



Openslide documentation can be found here: https://openslide.org
