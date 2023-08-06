# flamingo
<img src="https://ichef.bbci.co.uk/news/800/cpsprodpb/0C5B/production/_97436130_gettyimages-508496270-1.jpg" alt="From Wikipedia" height="150" align="right" caption="Text left hanging">

#### Extract annotations from .ndpa files and map on to the .ndpi image for use in other applications

* * *

## Install
```Python
conda create --name ndpi python=3.10
conda activate ndpi
python3 -m pip install openslide-python
conda install jupyterlab numpy pandas matplotlib scipy scikit-learn scikit-image
jupyer-lab

conda install libiconv # ???
conda install -c conda-forge openslide
conda install -c conda-forge openslide-python # probably better than the command above
```

Openslide documentation can be found here: https://openslide.org
