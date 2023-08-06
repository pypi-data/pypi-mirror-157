from cmath import inf
from copy import deepcopy
from typing import List
from util import Sol, get_x, get_lengths

class State:
    def __init__(self, a, t):
        self.a = a
        self.t = t

    def __hash__(self):
        return hash((str(self.a), self.t))

    def __eq__(self, other):
        return (str(self.a), self.t) == (str(other.a), other.t)

# check if lengths l is feasible, M = {0,1)^(size(X)) records if an agent is marked or not
# Moreover, if it is feasible, record the p and y for Sol
def feasible(a, t, l, x, sol, X, r, T, dp_table):
    if State(a, t) in dp_table:
        if(dp_table[State(a, t)][0]):
            sol = Sol(X, T, r, dp_table[State(a, t)][1])  #if feasible, update the sol
            return True
        else:
            return False
    tmp_a = deepcopy(a)
    n = len(x)
    intervals = []
    for a_item in a:
        if a_item!=-1:
            intervals.append([x[a_item], x[a_item]+l])
    res = False
    k = 0
    leave_at_t = t-r+1
    should_check = leave_at_t>=0
    ori_p = deepcopy(sol.p)
    prev_update_M = []
    if should_check:
        M = [0]*len(X[leave_at_t])
        for i in range(len(X[leave_at_t])):
            for j in range(len(intervals)):
                if X[leave_at_t][i] >= intervals[j][0] and X[leave_at_t][i] <= intervals[j][1] and M[i]==0:
                    M[i] = 1
                    sol.p[leave_at_t][i] = t-len(intervals)+j
        prev_update_M = deepcopy(M)
    while (not res) and 0 <= k and k < n:
        M = deepcopy(prev_update_M)
        if should_check:
            for i in range(len(X[leave_at_t])):
                if X[leave_at_t][i] >= x[k] and X[leave_at_t][i] <= x[k]+l and M[i]==0:
                    M[i] = 1
                    sol.p[leave_at_t][i] = t
            if sum(M) == len(M): #if all agents leaves at t are marked
                if t == T+r-2:
                    res = True
                else:
                    if (len(tmp_a)>0):
                        tmp_a.pop(0)
                        tmp_a.append(k)
                    res = feasible(tmp_a, t+1, l, x, sol, X, r, T, dp_table)
        else:
            if (len(tmp_a)>0):
                    tmp_a.pop(0)
                    tmp_a.append(k)
            res = feasible(tmp_a, t+1, l, x, sol, X, r, T, dp_table)
        k+=1
    if (not res):
        sol.p = ori_p
        dp_table[State(a, t)] = (res, None)
    else:
        sol.update_y((2*x[k-1]+l)/2, t)
        dp_table[State(a, t)] = (res, Sol(X, T, r, sol))
    return res


def mc_nfcfs(T, r, X):
    x = get_x(X)
    lengths = get_lengths(X)
    min_l = inf
    best_sol = Sol(X, T, r)
    for l in lengths:
        a = [-1]*(r-1)
        cur_sol = Sol(X, T, r)
        dp_table = {}  # empty dictionary to store the table
        res = feasible(a, 0, l, x, cur_sol, X, r, T, dp_table)
        if res and l < min_l:
            min_l = l
            best_sol = cur_sol
            break
    best_sol.maxcost = l/2

    return best_sol
