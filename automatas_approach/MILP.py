# imports
from gurobipy import *
import numpy

#########mockup #################
nodes = {0: "root", 1: "uno", 2: "dos", 3: "tres"}
states = {0: None, 1: None, 2: None, 3: None}
Sigma_dict = {0: (1, 0, 1), 1: (1, 1, 1), 2: (0, 1, 0), 3: (0, 0, 1)}
#########mockup #################

# número de nodos del arbol
N = range(len(nodes))
# número máximo de estados del automata. lo ideal es ocupar menos
Q = range(len(states))
# conjunto de
Sigma = range(len(Sigma_dict))

root = 0

# modelo
modelo = Model("Asignacion_de_estados")

# variables
x = modelo.addVars(N, Q, vtype=GRB.BINARY, name="x_nq")
delta = modelo.addVars(Q, Sigma, Q, vtype=GRB.BINARY, name="delta_qnq")
c = modelo.addVar(vtype=GRB.CONTINUOUS, name="c")

## instanciar modelo
## restricciones (1)
r_1 = modelo.addConstrs(
    (quicksum(x[n, q] for q in Q) == 1 for n in N), name="R(1)"
)
## restriccion (2)
r_2 = modelo.addConstr((x[root, 0] == 1), name="R(2)")
## restricciones (3)
r_3 = modelo.addConstrs(
    (
        quicksum(delta[q, sigma, qp] for qp in Q) == 1
        for sigma in Sigma
        for q in Q
    ),
    name="R(3)",
)

############################## TODO: es delicado porque tengo que hacer referencia al padre y a los simbolos
# # ## restricciones (5)
# r_5 = modelo.addConstrs(
#     (
#         x[p(n), q] + x[n, qp] -1 <= delta[q, s(n), qp]
#         for n in set(N).difference(set([root,]))
#         for q in Q
#         for qp in Q
#     ), name='R(5)'
# )
##############################

# Restriccion adicional para el indice
r_0 = modelo.addConstrs( (q * x[n,q] <= c for n in N for q in Q ), name="R(0)")

# setear funcion objetivo
modelo.setObjective(c, GRB.MINIMIZE)

# detalles

# optimizar
modelo.optimize()

# ver resultados
for i in x:
    print(i,x[i].X)