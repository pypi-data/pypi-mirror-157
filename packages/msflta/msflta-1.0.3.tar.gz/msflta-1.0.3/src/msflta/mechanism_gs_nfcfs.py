from util import Sol
from util import get_x
from statistics import median_low

def gs_nfcfs(T, r, X):
    x = get_x(X)
    sol = Sol(X, T, r)
    if r == 1:
        prev_y = 0
        for i in range(T):
            cur_y = median_low(X[i])
            sol.update_y(cur_y, i)
            sol.addCost(sum(map(lambda e: abs(e-cur_y), X[i])))
            sol.addCost(abs(cur_y - prev_y))
            for j in range(len(X[i])):
                sol.p[i][j] = i
            prev_y = cur_y
    else:
        left = min(x)
        right = max(x)
        mid = (left+right)/2
        is_left = True
        for i in range(T+1):
            if i > 0 and i!=T:
                W = [e for e in X[i] if (is_left and e < mid) or (not is_left and e>=mid)]
                W.extend([e for e in X[i-1] if (is_left and e < mid) or (not is_left and e>=mid)])
                for j in range(len(X[i])):
                    if (is_left and X[i][j] < mid) or (not is_left and X[i][j]>=mid):
                        sol.p[i][j] = i
                for j in range(len(X[i-1])):
                    if (is_left and X[i-1][j] < mid) or (not is_left and X[i-1][j]>=mid):
                        sol.p[i-1][j] = i
                sol.update_y(left if is_left else right, i)
                sol.addCost(sum(map(lambda e: abs(e-sol.y[i]), W)))
                sol.addCost(right-left)
            elif i == 0:
                W = [e for e in X[i] if (is_left and e < mid) or (not is_left and e>=mid)]
                for j in range(len(X[i])):
                    if (is_left and X[i][j] < mid) or (not is_left and X[i][j]>=mid):
                        sol.p[i][j] = i
                sol.update_y(left if is_left else right, i)
                sol.addCost(sum(map(lambda e: abs(e-sol.y[i]), W)))
                sol.addCost(left)
            
            else:
                W = [e for e in X[i-1] if (is_left and e < mid) or (not is_left and e>=mid)]
                for j in range(len(X[i-1])):
                    if (is_left and X[i-1][j] < mid) or (not is_left and X[i-1][j]>=mid):
                        sol.p[i-1][j] = i
                sol.update_y(left if is_left else right, i)
                sol.addCost(sum(map(lambda e: abs(e-sol.y[i]), W)))
                sol.addCost(right-left)
            is_left = not is_left
    return sol

X = [[1,5], [3,100], [101,200]]
T = 3
r = 2
sol = gs_nfcfs(T, r, X)
print(sol)