# TCLR package 
TCLR, Version 1, October, 2021. 

Tree-Classifier for Linear Regression (TCLR) is a novel Machine learning model to capture the functional relationships between features and a target based on correlation.

Reference paper : Cao B, Yang S, Sun A, Dong Z, Zhang TY. Domain knowledge-guided interpretive machine learning - formula discovery for the oxidation behaviour of ferritic-martensitic steels in supercritical water. J Mater Inf 2022. 

Doi : http://dx.doi.org/10.20517/jmi.2022.04

Written using Python, which is suitable for operating systems, e.g., Windows/Linux/MAC OS etc.

## Installing 
    pip install TCLR 

## Updating 
    pip install --upgrade TCLR

## Running 

```
from TCLR import TCLRalgorithm as model
dataSet = "testdata.csv" # dataset name
correlation = 'PearsonR(+)'
minsize, threshold, mininc = 3, 0.9, 0.01
model.start(dataSet, correlation, minsize, threshold, mininc, gplearn = True)
```

output: 
+ classification structure tree in pdf format（Result of TCLR.pdf) 
+ a folder called 'Segmented' for saving the subdataset of each leaf (passed test) 

note: 

the complete execution template can be downloaded at the *Source Code* folder 

**graphviz** (recommended installation) package is needed for generating the graphical results, which can be downloaded from the official website http://www.graphviz.org/. see user guide.


## Update log
TCLR V1.1 April, 2022. 
*debug and print out the slopes when Pearson is used*

TCLR V1.2 May, 2022.
*Save the dataset of each leaf*

TCLR V1.3 Jun, 2022.
*Para: minsize - Minimum unique values for linear features of data on each leaf (Minimum number of data on each leaf before V1.3)*

TCLR V1.4 Jun, 2022.
*Integrated symbolic regression algorithm of gplearn package.
Derive an analytical formula between features and solpes by gplearn*

## About 
Maintained by Bin Cao. Please feel free to open issues in the Github or contact Bin Cao
(bcao@shu.edu.cn) in case of any problems/comments/suggestions in using the code. 

