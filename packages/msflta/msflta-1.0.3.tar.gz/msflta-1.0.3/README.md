# Multi-stage Facility Location Problem with Transient Agent _(MSFL-TA)_

The **_msfl_ta_** is a package implementing several optimal algorithms and strategy-proof mechanisms introduced in the paper **_Multi-stage Facility Location Problem with Transient Agent_**. 

## Installation  

You can install the **_msflta_** from [PyPI](https://pypi.org/project/realpython-reader/):  

```python
python -m pip install msflta
```

The package requires a Python 3.7 and above and a Numpy 1.21.5 and above.

## Introduction

The package implements 6 different optimal algorithms and 4 different strategy-proof mechanisms as introduced in the paper.  

### Optimal Algorithms

* **sc_nfcfs** module - **sc_nfcfs(T, r, X)** function: implements the optimal algorithm for the "_No First Come First Serve Without Moving Cost Model_" in terms of _social cost_ objective
* **sc_wfcfs** module - **sc_wfcfs(T, r, X)** function: implements the optimal algorithm for the "_With First Come First Serve Without Moving Cost Model_" in terms of _social cost_ objective  
* **mc_nfcfs** module - **mc_nfcfs(T, r, X)** function: implements the optimal algorithm for the "_No First Come First Serve Without Moving Cost Model_" in terms of _maximum cost_ objective
* **mc_wfcfs** module - **mc_wfcfs(T, r, X)** function: implements the optimal algorithm for the "_With First Come First Serve Without Moving Cost Model_" in terms of _maximum cost_ objective  
* **sc_nfcfs_mov** module - **sc_nfcfs_mov(T, r, X)** function: implements the optimal algorithm for the "_No First Come First Serve With Moving Cost Model_" in terms of _social cost_ objective
* **sc_wfcfs_mov** module - **sc_wfcfs_mov(T, r, X)** function: implements the optimal algorithm for the "_With First Come First Serve With Moving Cost Model_" in terms of _social cost_ objective  

### Strategy-proof Mechanisms

* **mechanism_fc_nfcfs** module - **fc_nfcfs(T, r, X)** function: implements the strategy-proof mechanism named **Full-Coverage** for the "_Without First Come First Serve Without Moving Cost Model_"

* **mechanism_fc_wfcfs** module - **fc_wfcfs(T, r, X)** function: implements the strategy-proof mechanism named **Full-Coverage** for the "_With First Come First Serve Without Moving Cost Model_"

* **mechanism_gs_nfcfs** module - **gs_nfcfs(T, r, X)** function: implements the strategy-proof mechanism named **Full-Coverage** for the "_Without First Come First Serve With Moving Cost Model_"

* **mechanism_gs_wfcfs** module - **gs_wfcfs(T, r, X)** function: implements the strategy-proof mechanism named **Full-Coverage** for the "_With First Come First Serve With Moving Cost Model_"

## How to Use

For detailed **Input** and **Output** as well as the example of usage. Please refer to the [_Project Page_](https://github.com/William-WANG2/FYP-CityU)

