# Multi-stage Facility Location Problem with Transient Agent _(MSFL-TA)_

The **_msfl_ta_** is a package implementing several optimal algorithms and strategy-proof mechanisms introduced in the paper **_Multi-stage Facility Location Problem with Transient Agent_**. 

For more details about the algorithms, strategy-proof mechanisms, specifications on the concepts and terminologies in game theory community, you may later refer to the full paper to be published on [**AAAI 23**](https://aaai.org/Conferences/AAAI-23/) or the final year project report. 

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

### Input

* $T \in \mathbb{N}$ (an integer in Python) is the total number of stages where agents can arrive

* $r \in \mathbb{N}$ (an integer in Python) is the _tolerance rate_, indicating the number of stage(s) agents are willing to stay

* $X$ is a nexted list in python, i.e., a list contains several sublists, where the $i^{th}$ sublist contains the location information for agents arriving at stage $i$ .       

  ( **Important Notice: All the sublist should be sorted in ascending order!** ) 

$$
\begin{align*}
	X = [X_1, \ldots, X_{T}], \text{ where } X_{t} \in \mathbb{R}^{N_{t}} \text{ and } N_{t} \text{ is the total number of agents arriving at stage } t
\end{align*}
$$

For example, 

$T = 2, r = 2, X = [[1, 3, 4, 5], [2, 4, 6]]$ is a valid input. In this case, there are in total $2$ stages agents can arrive, and the tolerace rate is $2$. The agents arrive at $1^{st}$ stage are located at $1, 3, 4, 5$ where those arrive at $2^{nd}$ stage are located at $2, 4, 6$

### Output

The output of all the algorithm is an Instance of Class _Sol_.

* $Sol.p$  is a $2d$ List, where $Sol.p[t][i] = k$ indicates the $i^{th}$ agent arriving at stage $t$ is served at stage $k$.
* Sol.y is a $1d$ List, where $Sol.y[t] = loc$ indicates that the facility at stage $t$ is located at position $loc$.
* $Sol.cost$ is the social cost which can be retrieved when the objective function is the social cost, i.e. the total connecting cost of agents (+ the moving cost of the facility).
* $Sol.maxcost$ is the maximum cost which can be retrieved when the objective function is the maximum cost, i.e., the largest distance between an agent and the facility that serves him or her.

