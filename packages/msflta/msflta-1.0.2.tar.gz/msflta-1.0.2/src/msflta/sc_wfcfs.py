from cmath import inf
from copy import deepcopy
from pickle import NONE
from util import Sol
from statistics import median_low


class State_A:
    def __init__(self, i, j):
        self.i = i
        self.j = j

    def __hash__(self):
        return hash((self.i, self.j))

    def __eq__(self, other):
        return (self.i, self.j) == (other.i, other.j)

class State_compute:
    def __init__(self, t, e, i, j):
        self.t = t
        self.e = e
        self.i = i
        self.j = j

    def __hash__(self):
        return hash((self.t, self.e, self.i, self.j))

    def __eq__(self, other):
        return (self.t, self.e, self.i, self.j) == (other.t, other.e, other.i, other.j)

class Sol_A:
    def __init__(self, j, sol_A=None):
        if(sol_A == None):
            self.y = [0]*j
            self.serve_idx = [0]*j
            self.cost = 0
        elif(sol_A != None):
            self.cost = sol_A.cost
            self.y = deepcopy(sol_A.y)
            self.serve_idx = deepcopy(sol_A.serve_idx)

    def update_y(self, t, loc):
        self.y[t] = loc

    def update_serve_idx(self, t, idx):
        self.serve_idx[t] = idx

    def add_cost(self, cost):
        self.cost+=cost

# i is the index of W starting from 0
# j is the ramaining stage used to serve agents
# start_idx is the strating index of the first element in W corresponding to the original agent set
# stage is the arrival stage of the agents in W
def A(W, i, j, sol_A, dp_table):
    if State_A(i, j) in dp_table:
        return Sol_A(None, dp_table[State_A(i, j)])
    if(i < 0):  # No agent is left in W
        if(j != 0):  # There is some assigned stage to be used
            for k in range(j):
                sol_A.update_y(k, 0)
                sol_A.update_serve_idx(k, i)
        
        dp_table[State_A(i, j)] = Sol_A(None, sol_A)
        return sol_A
    else:
        if(j == 1):
            y = median_low(W[0:i+1])
            sol_A.update_y(j-1, y)
            sol_A.update_serve_idx(j-1, 0)
            sol_A.add_cost(sum(map(lambda x: abs(x-y), [x for x in W[0:i+1]])))
            
            dp_table[State_A(i, j)] = Sol_A(None, sol_A)
            return sol_A
        else:  
            ori_sol_A = Sol_A(None, sol_A)
            min_cost = inf
            best_sol_A = Sol_A(None, sol_A)

            for k in range(0,i+1):
                cur_y = median_low(W[k:i+1])
                cur_cost = sum(map(lambda x: abs(x-cur_y), [x for x in W[k:i+1]]))
                sol_A = A(W, k-1, j-1, sol_A, dp_table)
                if(cur_cost + sol_A.cost < min_cost):
                    best_sol_A = Sol_A(None, sol_A)
                    min_cost = cur_cost + sol_A.cost
                    best_sol_A.update_y(j-1, cur_y)
                    best_sol_A.update_serve_idx(j-1, k)
                    best_sol_A.add_cost(cur_cost)
                    sol_A = Sol_A(None, ori_sol_A)
            
            dp_table[State_A(i, j)] = Sol_A(None, best_sol_A)
            return best_sol_A

def compute(T, r, X, t, e, i, j, dp_table, sol):
    if State_compute(t,e,i,j) in dp_table:
        return Sol(X, T, r, dp_table[State_compute(t,e,i,j)])
    if e == 0:
        dp_A_table = {}
        sol_A = Sol_A(t)
        W = [w for idx, w in enumerate(X[e]) if idx<i or idx>=j]
        W_idx = [idx for idx, w in enumerate(X[e]) if idx<i or idx>=j]
        sol_A = A(W, len(W)-1, t, sol_A, dp_A_table)
        sol.addCost(sol_A.cost)
        prev_idx = len(W)
        for stage in reversed(range(t)):
            sol.update_y(sol_A.y[stage], stage)
            idx = sol_A.serve_idx[stage] 
            for update_idx in range(idx, prev_idx):
                sol.p[e][W_idx[update_idx]] = stage 
            prev_idx = idx
        dp_table[State_compute(t,e,i,j)] = Sol(X, T, r, sol)
        return sol
    elif t == 1:
        W = []
        for stage in range(e+1):
            if stage == e:
                W.extend([w for idx, w in enumerate(X[stage]) if idx<i or idx>=j])
            else:
                W.extend(X[stage])
        cur_y = median_low(W)
        sol.addCost(sum(map(lambda x: abs(x-cur_y), [x for x in W])))
        sol.update_y(cur_y, t-1)
        for stage in range(e+1):
            if stage == e:
                for idx in [valid_idx for valid_idx in range(len(X[stage])) if valid_idx < i or valid_idx >= j]:
                    sol.p[stage][idx] = t-1
            else:
                for idx in range(len(X[stage])):
                    sol.p[stage][idx] = t-1
        dp_table[State_compute(t,e,i,j)] = Sol(X, T, r, sol)
        return sol
    else:
        ori_sol = Sol(X, T, r, sol)
        min_cost = inf
        best_sol = Sol(X, T, r, sol)
        for e_ in range(e):
            ab_pair = []
            for a in range(j, len(X[e])+1):
                for b in range(a, len(X[e])+1):
                    ab_pair.append([a, b])
            for b in range(0, i):
                for a in range(0, b+1):
                    ab_pair.append([a, b])
            i_j_pair = []
            for i_ in range(len(X[e_])+1):
                for j_ in range(i_, len(X[e_])+1):
                    if (not (i_==0 and j_==len(X[e_]))):
                        i_j_pair.append([i_, j_])
            for a, b in ab_pair:
                for i_, j_ in i_j_pair:
                    I_1 = 0 if a==0 and b==i+1 and j==len(X[e]) else 1
                    I_2 = 0 if e_ == e-1 and a == b and i_ == j_ else 1
                    I_3 = 0 if i_== j_ else 1
                    I_4 = 0 if a== b else 1
                    for t_ in range(max(e-1+I_4, e_+I_2)+1, min(e_+r+I_2-I_3, t-I_1)+1):
                        sol = Sol(X, T, r, ori_sol)
                        # recursion cost
                        sol = compute(T, r, X, t_-I_2, e_, i_, j_, dp_table, sol)
                        #g function cost
                        W_g = []
                        for stage in range(e_+1, e):
                            W_g.extend(X[stage])
                            for idx in range(len(X[stage])):
                                sol.p[stage][idx] = t_-1
                        W_g.extend(X[e][a:b])
                        for idx in range(a,b):
                            sol.p[e][idx] = t_-1
                        W_g.extend(X[e_][i_:j_])
                        for idx in range(i_,j_):
                            sol.p[e_][idx] = t_-1
                        if(I_2 != 0):
                            cur_y_g = median_low(W_g)
                            sol.addCost(sum(map(lambda x: abs(x-cur_y_g), [x for x in W_g])))
                            sol.update_y(cur_y_g, t_-1)
                        #A function cost
                        if(I_1==0):
                            for stage in range(t_+1, t+1):
                                sol.update_y(0, stage-1)
                        else:
                            sol_A = Sol_A(t-t_)
                            dp_A_table = {}
                            W_A = [w for idx, w in enumerate(X[e]) if idx not in range(a, b) and idx not in range(i, j)]
                            W_A_idx = [idx for idx, w in enumerate(X[e]) if idx not in range(a, b) and idx not in range(i, j)]
                            sol_A = A(W_A, len(W_A)-1, t-t_, sol_A, dp_A_table)
                            sol.addCost(sol_A.cost)
                            prev_idx = len(W_A)
                            for stage in reversed(range(t_+1, t+1)):
                                sol.update_y(sol_A.y[stage-(t_+1)], stage-1)
                                if len(W_A) > 0:
                                    idx = sol_A.serve_idx[stage-(t_+1)] 
                                    for update_idx in range(idx, prev_idx):
                                        sol.p[e][W_A_idx[update_idx]] = stage-1 
                                    prev_idx = idx
                        if(sol.cost < min_cost):
                            min_cost = sol.cost
                            best_sol = Sol(X, T, r, sol)
        dp_table[State_compute(t,e,i,j)] = Sol(X, T, r, best_sol)
        return best_sol                  


def sc_wfcfs(T, r, X):
    t = T+r-1
    e = T-1
    i = 0
    j = 0
    dp_table = {}
    sol = Sol(X, T, r)
    sol = compute(T, r, X, t, e, i, j, dp_table, sol)
    return sol


