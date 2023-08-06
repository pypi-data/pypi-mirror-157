from cmath import inf
from typing import List
from util import Sol, get_x, get_lengths

class State:
    def __init__(self, a, t, s):
        self.a = a
        self.t = t
        self.s = s

    def __hash__(self):
        return hash((self.a, self.t, self.s))

    def __eq__(self, other):
        return (self.a, self.t, self.s) == (other.a, other.t, self.s)

def num_of_cover(W, idx, l, sol, t, s):
    start_idx = 0
    num = 0
    while start_idx in range(len(W)):
        next_idx = start_idx
        while next_idx < len(W) and W[next_idx] <= W[start_idx]+l:
            sol.p[t][idx[next_idx]] = s+num
            next_idx+=1
        if (s+num < len(sol.y)):
            sol.update_y((2*W[start_idx]+l)/2, s+num)
        num+=1 
        start_idx = next_idx
    return num

def feasible(a, t, s, l, x, sol, X, r, T, dp_table):
    if State(a, t, s) in dp_table:
        if(dp_table[State(a, t, s)][0]):
            sol = Sol(X, T, r, dp_table[State(a, t, s)][1])  #if feasible, update the sol
            return (True, sol)
        else:
            return (False, None)
    if t == T:
        return (True, sol)
    M_t = [0]*len(X[t])
    res = False
    ori_sol = Sol(X, T, r, sol)
    if s-1 >= t:
        for i in range(len(X[t])):
            if X[t][i] >= x[a] and X[t][i] <= x[a]+l:
                M_t[i] = 1
                sol.p[t][i] = s-1
    if sum(M_t) == len(M_t):
        res = feasible(a, t+1, s, l, x, sol, X, r, T, dp_table)[0]
    else:
        n = len(x)
        k = 0
        while res == False and k in range(n):
            W = [w for index, w in enumerate(X[t]) if M_t[index] == 0 and not (w >= x[k] and w <= x[k]+l)]
            idx = [index for index, w in enumerate(X[t]) if M_t[index] == 0 and not (w >= x[k] and w <= x[k]+l)]
            num = num_of_cover(W, idx, l, sol, t, s)
            for i in range(len(X[t])):
                if X[t][i] >= x[k] and X[t][i] <= x[k]+l and M_t[i] == 0:
                    sol.p[t][i] = s+num
            if (s+num <= t+r-1):
                sol.update_y((2*x[k]+l)/2, s+num)
                res = feasible(k, t+1, s+num+1, l, x, sol, X, r, T, dp_table)[0]
            k+=1
    if(not res):
        sol = Sol(X, T, r, ori_sol)
        dp_table[State(a, t, s)] = (res, None)
        return (res, None)
    else:
        dp_table[State(a, t, s)] = (res, Sol(X, T, r, sol))
        return (res, Sol(X, T, r, sol))
        

def mc_wfcfs(T, r, X):
    x = get_x(X)
    lengths = get_lengths(X)
    min_l = inf
    best_sol = Sol(X, T, r)
    for l in lengths:
        a = -1
        cur_sol = Sol(X, T, r)
        dp_table = {}  # empty dictionary to store the table
        res = feasible(a, 0, 0, l, x, cur_sol, X, r, T, dp_table)
        if res[0] and l < min_l:
            min_l = l
            best_sol = cur_sol
            break
    best_sol.maxcost = l/2

    return best_sol
