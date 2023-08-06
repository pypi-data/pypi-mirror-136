# Differentially Private Release of High-Dimensional Datasets using the Gaussian Copula

Asghar, Hassan; Ding, Ming; Rakotoarivelo, Thierry; M'rabet, Sirine; Kaafar, Dali. Differentially Private Release of High-Dimensional Datasets using the Gaussian Copula. Journal of Privacy and Confidentiality. 2020; 10(2):1-38. http://hdl.handle.net/102.100.100/366470?index=1

### Introduction 

dpc is a library to efficiently release differentially private synthetic versions of high-dimensional datasets with high utility.generate differantial private datase.  The core technique in our mechanism is the use of copulas, which are functions representing dependencies among random variables with a multivariate distribution. 

This library includes three models:
- dpc-onehot : categorical attributes are converted to one hot binning. Gaussian copula is uded to define dependencies of attributes in the input dataset. Synthetic records are sampled through this copula.
- dpc : catagorical attributes are considered as discrete data in wich the order is chosen arbiterary. Gaussian copula is uded to define dependencies of attributes in the input dataset. Synthetic records are sampled through this copula.
- dpc-cond : run Baysesian network to capture the joint probability distribution of the attributes. Select n attributes having highest correlation and run dpc algorithm to create a skeleton. Synthetic records are sampled through a conditionnal algorithm using the skeleton.


### Installation
```
# Requires the latest pip
pip install --upgrade pip

# Current statble release
pip install -i https://test.pypi.org/simple/ dpcgeneration
```

Dpc Library  is tested and supported on the following 64-bit systems:
- Python 3.6
- Ubuntu 16.04 or later
- Mac Os 10.15 or later

### Get started
How to multiply one number by another with this lib:

```Python
from dpcgeneration import DPCopula
import pandas as pd
import numpy as np 
from dpcgeneration import calculate_oneWay, calculate_print, calculate_twoWay


# Create testfile with ramdom 0 and 1 
df = pd.DataFrame(np.random.randint(0,2,size=(100, 4)), columns=list('ABCD'))

# Instantiate a Multiplication object
copula = DPCopula()

# Run dpc_bin algorith with epsilon=1 
df_res = copula.rundpc_bin(data=df,withNoise=True, epslimit=1,path_fnl='../out/',labels=['dpc-bin'],convert_bin=False, verbose=True)

#plot one-way and two-way absolute error between original and generated dataset 
df.columns = df.columns.astype(str)
df_res = df_res.astype(int)
#One way error
df_oneway_orig = calculate_oneWay(df,df.columns.tolist()[5:10])
df_oneway_gen= calculate_oneWay(df_res, df_res.columns.tolist())
calculate_print([df_oneway_orig], [df_oneway_gen], 'CDF of One Way', labels=['5 onehot encoding attributes'],
                                                     figname='../out/'+'mnist0-oneway', printgraph=False, savedata='../out2/'+'mnist0-oneway_gen')
#Two eay error
df_twoway_orig = calculate_twoWay(df, df.columns.tolist()[5:10])
df_twoway_gen = calculate_twoWay(df_res, df_res.columns.tolist())
calculate_print([df_twoway_orig], [df_twoway_gen], 'CDF of Two Way', labels=['5 onehot encoding attributes'],
                                                    figname='../out/'+'mnist0-twoway', printgraph=False, savedata='../out2/'+'mnist0-twoway_gen')


```

![Alt text](https://bitbucket.csiro.au/projects/ISPGROUP/repos/dpc_generation/browse/out/mnist0-oneway0.png?raw=true "oneway")

![Alt text](https://bitbucket.csiro.au/projects/ISPGROUP/repos/dpc_generation/browse/out/mnist0-twoway0.png?raw=true "twoway")

