from cmath import inf
from copy import deepcopy
import numpy as np
from itertools import product
from util import Agent, Sol, get_x

class Next_state:
    def __init__(self, M_, idx):
        self.M_ = M_
        self.idx = idx


class State:
    def __init__(self, M_, t, p):
        self.M_ = M_
        self.t = t
        self.p = p

    def __hash__(self):
        return hash((str(self.M_), self.t, self.p))

    def __eq__(self, other):
        return (str(self.M_), self.t, self.p) == (str(other.M_), other.t, self.p)


def transform_to_agent(idx_shift, round, idx_loc) -> Agent:
    idx, loc = idx_loc
    return Agent(round, idx+idx_shift, loc)


def construct_split(X, r, split: list, idx, t, temp: list, is_start: bool):
    if(r == 0):
        split.append(temp)
    elif(r == 1):
        ori = deepcopy(temp)
        # temp.append(X[t-1][idx:])
        temp.append(
            list(map(transform_to_agent, [idx]*(len(X[t-1])-idx), [t]*(len(X[t-1])-idx), enumerate(X[t-1][idx:]))))
        construct_split(X, r-1, split, r, t, temp, is_start)
        temp = ori
    else:
        for i in range(idx, len(X[t-1])+1):
            ori = deepcopy(temp)
            # temp.append(X[t-1][idx:i])
            temp.append(
                list(map(transform_to_agent, [idx]*(len(X[t-1])-idx), [t]*(i-idx), enumerate(X[t-1][idx:i]))))
            construct_split(X, r-1, split, i, t, temp, is_start)
            temp = ori


def split(T, r, X):
    splits = []
    for t in range(1, T+1):
        split = []
        construct_split(X, r, split, 0, t, [], True)
        splits.append(split)
    return product(*splits)


# a = split(3, 2, [[3, 4, 5, 6], [7, 8, 9, 10], [1, 2]])
# split returns arr[ [all consecutive [r splittings agents of stage 1] ], [all consecutive [r splittings agents of stage 2] ], ...]
# for a_item in a:
#     print(a_item)


# get all possible M' for next recursion given current M
def get_M_(M, start, t):
    T = len(M)
    M_ = np.array(M)
    M_ = np.transpose(np.nonzero(M_ == 0)).tolist()
    M_nonzero = []
    for i in range(start, t+1):
        M_t = [e[1] for e in M_ if e[0] == i]
        if not M_t:
            M_t = [-1]  # -1 indicates that there is no 0 element
        M_nonzero.append(M_t)
    M_nonzero_idx = product(*M_nonzero)
    M_ = []
    changed_idx = []
    for M_nonzero_idx_item in M_nonzero_idx:
        item = []
        changed_idx_item = []
        for i in range(T):
            cur_changed_idx = 0
            if (start <= i and i <= t):
                cur_changed_idx = M_nonzero_idx_item[i-start]
                changed_idx_item.append(cur_changed_idx)
                item.append([1 if (e == 1 or idx == cur_changed_idx)
                            else 0 for idx, e in enumerate(M[i])])
            else:
                item.append(M[i])
        M_.append(item)
        changed_idx.append(changed_idx_item)
    return Next_state(M_, changed_idx)


def compute(S, M, T, r, t, X, dp_table, x_y0, p) -> Sol:
    if State(M, t, p) in dp_table:
        return dp_table[State(M, t, p)]
    else:
        if(t == T+r-1):
            return Sol(X, T, r)
        else:
            start = max(t-r+1, 0)
            next_state = get_M_(M, start, t)
            best_cost = inf
            best_sol = Sol(X, T, r)
            n = len(x_y0)
            for M_, idx in zip(next_state.M_, next_state.idx):
                for p_ in range(n):
                    later_sol = compute(S, M_, T, r, t+1, X, dp_table, x_y0, p_)
                    cur_sol = Sol(X, T, r, later_sol)
                    agents = []
                    for i in range(start, min(t+1, T)):
                        if idx[i-start] != -1:
                            agents += S[i][idx[i-start]]
                    fac = x_y0[p_] 
                    cur_cost = abs(x_y0[p] - x_y0[p_])
                    if(len(agents) > 0):
                        cur_cost += Agent.cost(agents, fac)
                    if(later_sol.cost+cur_cost <= best_cost):
                        best_cost = later_sol.cost+cur_cost
                        cur_sol.addCost(cur_cost)
                        cur_sol.update_y(fac, t)
                        for agent in agents:
                            cur_sol.update_p(agent.round, agent.idx, t)
                        best_sol = cur_sol
            dp_table[State(M, t, p)] = best_sol
            return best_sol


def sc_nfcfs_mov(T, r, X):
    splittings = split(T, r, X)
    best_sol = Sol(X, T, r)
    x = get_x(X)
    best_cost = inf
    for S in splittings:
        dp_table = {}  # empty dictionary to store the table
        M = [[0] * r for _ in range(T)]
        x.append(0)
        sol = compute(S, M, T, r, 0, X, dp_table, x, len(x)-1)
        if(sol.cost < best_cost):
            best_cost = sol.cost
            best_sol = sol
    return best_sol

