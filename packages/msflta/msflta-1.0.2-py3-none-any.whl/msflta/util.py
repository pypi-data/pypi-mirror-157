from copy import deepcopy
from statistics import median_low
from typing import List

class Sol:
    def __init__(self, X, T, r, sol=None):
        self.cost = 0
        self.maxcost = 0
        self.p = deepcopy(X)
        self.y = [0]*(T+r-1)
        if(sol != None):
            self.cost = sol.cost
            self.p = deepcopy(sol.p)
            self.y = deepcopy(sol.y)

    def addCost(self, c):
        self.cost += c

    def update_p(self, t, i, round):
        self.p[t-1][i] = round

    def update_y(self, loc, t):
        self.y[t] = loc
    
    def update_maxcost(self, maxcost):
        self.maxcost = maxcost


class Agent:
    def __init__(self, round, idx, loc):
        self.round = round  # starting from 1: 1 to T
        self.idx = idx  # idx starting from 0
        self.loc = loc

    @staticmethod
    def med(agents) -> float:
        return median_low([x.loc for x in agents])

    @staticmethod
    def cost(agents, agents_loc) -> float:
        cost = sum(map(lambda x: abs(x-agents_loc), [x.loc for x in agents]))
        return cost

# Get all agents' locations
def get_x(X: List) -> List:
    x = [X_stage_item for X_stage in X for X_stage_item in X_stage]
    x = list(set(x))
    x.sort()
    return x

# Get all possible interval lengths
def get_lengths(X: List) -> List:
    x = [X_stage_item for X_stage in X for X_stage_item in X_stage]
    dis = []
    for i in range(len(x)):
        for j in range(i+1, len(x)):
            dis.append(abs(x[i]-x[j]))
    dis = list(set(dis))
    dis.sort()
    return dis

