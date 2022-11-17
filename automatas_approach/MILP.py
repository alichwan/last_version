# imports
from gurobipy import *
import numpy

# costos y dominio
n_states = 4
Q = range(n_states)
N = range(n_states)
T = range(n_states)
Sigma = range(n_states)

lambda_e = 1
lambda_t = 1
lambda_pos = 1
lambda_neg = 1
c_pos = lambda n: 1
c_neg = lambda n: 1

# modelo
modelo = Model("Asignacion_de_estados")

# variables
x = modelo.addVars(N, Q, vtype=GRB.BINARY, name="x_nq")
delta = modelo.addVars(Q, Sigma, Q, vtype=GRB.BINARY, name="delta_qnq")
c = modelo.addVars(N, lb=-float("inf"), name="c_n")
e = modelo.addVars(Q, Sigma, lb=-float("inf"), name="e_qsigma")
t = modelo.addVars(N, lb=-float("inf"), name="t_n")

## instanciar modelo
## restricciones (1)
r_1 = modelo.addConstrs(
    (quicksum(x[n, q] for q in Q) == 1 for n in N), name="R(1)"
)
## restriccion (2)
r_2 = modelo.addConstr((x[r, 0] == 1), name="R(2)")
## restricciones (3)
r_3 = modelo.addConstrs(
    (
        quicksum(delta[q, sigma, qp] for qp in Q) == 1
        for sigma in Sigma
        for q in Q
    ),
    name="R(3)"
)
## restricciones (4)
r_4 = modelo.addConstrs(
    (delta[q, sigma, q] == 1 for q in T for sigma in Sigma), name="R(4)"
)
# ## restricciones (5)
# r_5 = modelo.addConstrs(, name='R(5)')
# ## restricciones (6)
# r_6 = modelo.addConstrs(, name='R(6)')
# ## restricciones (7)
# r_7 = modelo.addConstrs(, name='R(7)')
# ## restricciones (8)
r_8 = modelo.addConstrs(
  (quicksum(x[n,q] for q in set(Q).difference(set(T))) == t[n] for n in N)
  , name='R(8)'
)

# setear funcion objetivo
modelo.setObjective(
    (
        quicksum(c[n] for n in N)
        + quicksum(lambda_e * e[q, sigma] for sigma in Sigma for q in Q)
        + quicksum(lambda_e * quicksum(t[n] for n in N))
    ),
    GRB.MINIMIZE
)

# detalles

# optimizar
modelo.optimize()

# ver resultados
