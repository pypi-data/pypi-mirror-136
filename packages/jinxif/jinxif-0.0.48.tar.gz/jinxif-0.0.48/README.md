
# cmIF fork: jinxIF version 0.0.0

+ Author: engje, bue
+ Date: 2020-11-01
+ License: GPLv3
+ Language: Python3

Description: jinxIF is a fork from Jennifer Eng's original cmIF mplex\_image software library (https://gitlab.com/engje/cmif).
cmIF is a Python3 library for automated image processing and analysis of multiplex immunofluorescence images.

Source: the latest version of this user manual can be found at https://gitlab.com/bue/jinxif/-/blob/master/README.md


## HowTo - Installation

**Python version:**

A cornerstone of jinxif is **cellpose**, which is used for segmentation.
Cellpose requires at the moment of this writing python version 3.8.
We set the python requirement for jinxif accordingly in the setup.py. 
You can check if these requirements are still true (https://github.com/MouseLand/cellpose/blob/master/environment.yml).
If this has changes, please drop us a line, that we can adjust the setup.py file. Thank you!

**Python enviromnet:**

We recommend to install jinxif in an own python environment.
Iff you run miniconda (or anaconda) you can generate a jinxif python environment like this:
```bash
conda create -n jinxif python=3.8
```
You can activat the generated jinxif envioment like this
```bash
conda activate jinxif
```

**CPU based installation:**

1. install some basics.
```bash
pip install ipython jupyterlab
```

2. install tourch.

check yout the pytourch side (https://pytorch.org/get-started/locally/),
if you want to install tourch whith pip, LibTourch, or from source, rather then with conda.
```bash
conda install pytorch
```

3. install cellpose.
```bash
pip install cellpose
```

4. install jinxif.
```bash
pip install jinxif
```

**Nvidia GPU based installation:**

1. install some basics.
```bash
conda install ipython jupyterlab
```

2. install tourch.

Note: For running touch on a GPU, you have to know which cuda toolkit version you have installed on your machine.
How is depening on your operating system. We leave it up to you to figure out how to do that.

Please go to the pytorch side (https://pytorch.org/get-started/locally/) to figure out for the latest version of torch, what has to be installed, for the related os, conda, python, cuda setting. **pytorch** is enough, **torchaudio** and **torchvision** is not needed.
The final installation command will look something like below.
```bash
conda install pytorch cudatoolkit=nn.n -c pytorch
```

3. install cellpose.

This is a bit special, because we want to install cellpose without dependencies, so that the CPU focused pip version of pytorch does not get installed!
You should use the same --no-deps --upgarde parameter when you try to update cellpose.
```bash
pip install --no-deps cellpose --upgrade
```

4. install jinxif.
```bash
pip install jinxif
```

## Tutorial

## Discussion

## References
