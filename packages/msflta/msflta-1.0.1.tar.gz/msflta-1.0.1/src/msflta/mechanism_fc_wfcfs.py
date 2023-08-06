from mc_nfcfs import mc_wfcfs
from util import Sol
from random import choice


def fc_nfcfs(T, r, X):
    sol = mc_wfcfs(T, r, X)
    radius = sol.maxcost
    new_sol = Sol(X, T, r, sol)
    left_or_right = [-1,1]
    for i in range(len(sol.y)):
        new_sol.update_y(sol.y[i] + choice(left_or_right)*radius, i)
    new_sol.maxcost = 2*radius
    return new_sol

