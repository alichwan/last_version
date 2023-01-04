# imports
from gurobipy import *
import numpy
# from main import God, read_json, generate_trace


def milp(arbol, max_states):
    #########mockup #################
    nodes = arbol.id_nodes
    Sigma_dict = {s: i for i, s in enumerate(arbol.Sigma)}
    rev_Sigma_dict = {i:s for s, i in Sigma_dict.items()}
    states = {i: None for i in range(max_states)}
    #########mockup #################

    # número de nodos del arbol
    N = range(len(nodes))
    # conjunto de
    Sigma_range = range(len(Sigma_dict))
    # número máximo de estados del automata. lo ideal es ocupar menos
    Q = range(len(states))

    root = 0

    # modelo
    modelo = Model("Asignacion_de_estados")

    # variables
    x = modelo.addVars(N, Q, vtype=GRB.BINARY, name="x_nq") # nodo n es mapeado a estado q
    delta = modelo.addVars(Q, Sigma_range, Q, vtype=GRB.BINARY, name="delta_qnq") # funcion de trancicion de automata
    f = modelo.addVars(Q, vtype=GRB.BINARY, name="f_q") # 1 ssi estado q es usado 
    c = modelo.addVar(vtype=GRB.CONTINUOUS, name="c") # funcion de costo auxiliar

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
            for sigma in Sigma_range
            for q in Q
        ),
        name="R(3)",
    )

    # # ## restricciones (5)
    r_5 = modelo.addConstrs(
        (
            x[arbol.parent(n), q] + x[n, qp] - 1
            <= delta[q, Sigma_dict[arbol.sigma(n)], qp]
            for n in list(N)[1:]
            for q in Q
            for qp in Q
        ),
        name="R(5)",
    )

    # Restriccion adicional para el indice
    r_0 = modelo.addConstrs((q * x[n, q] <= c for n in N for q in Q), name="R(0)")
    # r_0 = modelo.addConstrs((q * f[q] <= c for q in Q), name="R(0)")

    # Restriccion para forzar a rechazar los negativos y aceptar los positivos
    modelo.addConstrs((x[n, q] <= f[q]  for q in Q for n in arbol.F_pos()), name="aceptacion pos")
    modelo.addConstrs((x[n, q] <= 1-f[q]  for q in Q for n in arbol.F_neg()), name="aceptacion neg")

    # setear funcion objetivo
    modelo.setObjective(c, GRB.MINIMIZE)

    # optimizar
    modelo.optimize()
    return modelo, x, delta, c, f, rev_Sigma_dict



# TODO, agarrar los nodos del estado y graficar con libreria el automata
if __name__ == "__main__":
    p=2
    # connections = read_json("../traces_ch/B6ByNegPMKs_connectivity.json")
    # objects = read_json("../traces_ch/B6ByNegPMKs_objects.json")

    # all_traces = generate_trace(p, connections, objects)


    # g = God(all_traces)
    # arbol = g.give_me_the_plant()

    # if arbol.sat:
    #     modelo, x, delta, c, f = milp(arbol, max_states = 5)

    #     if modelo.Status == 2:
    #         # ver resultados    
    #         for i in x :
    #             if x[i].X > 0.2:
    #                 print(i, x[i].X)

    #         for q,s,qp in delta:
    #             if q != qp and delta[q,s,qp].X > 0.2:
    #                 print(f"({q},{s},{qp}), {delta[q,s,qp].X}")
    #     elif modelo.Status == 3:
    #         print("Modelo insatisfacible, ID de status:", modelo.Status)
    #     else:
    #         print("Ststus id: ", modelo.Status )

    # if not arbol.sat:
    #     print("arbol insatisfacible")