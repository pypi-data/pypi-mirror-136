# Differentially Private Release of High-Dimensional Datasets using the Gaussian Copula

Asghar, Hassan; Ding, Ming; Rakotoarivelo, Thierry; M'rabet, Sirine; Kaafar, Dali. Differentially Private Release of High-Dimensional Datasets using the Gaussian Copula. Journal of Privacy and Confidentiality. 2020; 10(2):1-38. http://hdl.handle.net/102.100.100/366470?index=1


## Installation
1. Install Anaconda for Python 3.6
```
conda create -n dpc python=3.6

```

2. Get the latest code.
 ```
 git clone https://bitbucket.csiro.au/scm/ispgroup/dpc_generation.git
 cd dpc_generation

```

3. In the dpc_generation project directory, create and activate the python environment:
```
conda-env create -f environment.yaml
conda activate dpc
```


4. Next, install the remaining dependencies:
```
python -m pip install -r requirements.txt
```

## How-to
To output synthetic data: run dpc.py

```
python dpc.py --help
Usage: dpc.py [OPTIONS]

Options:
  --dataset TEXT                  Input dataset: adult, mnist_9, transport
  --model TEXT                    dpc or dpc-onehot or dpc-cond.
  --dp_epsilon FLOAT              dp epsilon
  --output TEXT                   output repository
  --privbayes-degree-max INTEGER  privbayes degree max
  --extendoutput INTEGER          extend output
  --help                          Show this message and exit.
  
 ```
 
  Last updated 01/10/2021 by Sirine Mrabet
  sirine.mrabet@data61.csiro.au
