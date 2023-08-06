from util import Sol
from util import get_x
from random import choice

def gs_wfcfs(T, r, X):
    x = get_x(X)
    sol = Sol(X, T, r)
    left = min(x)
    right = max(x)
    mid = (left+right)/2
    radius = (left-right)/2
    left_or_right = [-1, 1]
    prev_y = 0
    for i in range(T):
        cur_y = mid+choice(left_or_right)*radius
        sol.update_y(cur_y, i)
        sol.addCost(sum(map(lambda e: abs(e-cur_y), X[i])))
        sol.addCost(abs(cur_y - prev_y))
        for j in range(len(X[i])):
            sol.p[i][j] = i
        prev_y = cur_y
    return sol

X = [[1,5], [3,100], [101,200]]
T = 3
r = 2
sol = gs_wfcfs(T, r, X)
print(sol)