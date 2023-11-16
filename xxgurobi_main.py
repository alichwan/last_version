"""
Module with the gurobi-logic
"""

from gurobipy import *


def milp(tree, max_states, verbose=0, timelimit=60 * 10):
    """Mixed Integer Linear Programming that solves the assignation problem

    Args:
        tree (PrefixTree): Structure that embed the prefix tree logic
        max_states (int): maximum number of states that can be used to build the solution automaton
        verbose (int, optional): 1 if gurobi should print whats going on internally. Defaults to 0.
        timelimit (int, optional): time limit in seconds to solve the problem. Defaults to 30 minutes .

    Returns:
        _type_: _description_
    """
    nodes = tree.id_nodes
    sigma_dict = {s: i for i, s in enumerate(tree.Sigma)}
    rev_sigma_dict = {i: s for s, i in sigma_dict.items()}
    states = {i: None for i in range(max_states)}

    # número de nodos del treeP
    n_nodes = range(len(nodes))
    # conjunto de
    sigma_range = range(len(sigma_dict))
    # número máximo de estados del automata. lo ideal es ocupar menos
    n_states = range(len(states))

    root = 0

    # modelo
    model = Model("Asignacion_de_estados")
    model.Params.OutputFlag = verbose
    model.setParam(GRB.Param.TimeLimit, int(timelimit))

    # variables
    n_to_q = model.addVars(
        n_nodes, n_states, vtype=GRB.BINARY, name="x_nq"
    )  # nodo n es mapeado a estado q
    delta = model.addVars(
        n_states, sigma_range, n_states, vtype=GRB.BINARY, name="delta_qnq"
    )  # funcion de trancicion de automata
    is_used = model.addVars(
        n_states, vtype=GRB.BINARY, name="f_q"
    )  # 1 ssi estado q es usado
    cost = model.addVar(vtype=GRB.CONTINUOUS, name="cost")  # funcion de costo auxiliar

    ## instanciar modelo
    ## restricciones (1)
    model.addConstrs(
        (quicksum(n_to_q[n, q] for q in n_states) == 1 for n in n_nodes),
        name="R(1)",
    )
    ## restriccion (2)
    model.addConstr((n_to_q[root, 0] == 1), name="R(2)")
    ## restricciones (3)
    model.addConstrs(
        (
            quicksum(delta[q, sigma, qp] for qp in n_states) == 1
            for sigma in sigma_range
            for q in n_states
        ),
        name="R(3)",
    )

    # # ## restricciones (5)
    def assignation(node, state1, state2):
        a_side = n_to_q[tree.parent(node), state1]
        b_side = n_to_q[node, state2]
        delta_side = delta[state1, sigma_dict[tree.sigma(node)], state2]
        return a_side + b_side - 1 <= delta_side

    model.addConstrs(
        (
            assignation(n, q, qp)
            for n in list(n_nodes)[1:]
            for q in n_states
            for qp in n_states
        ),
        name="R(5)",
    )

    # Restriccion adicional para el indice
    model.addConstrs(
        (q * n_to_q[n, q] <= cost for n in n_nodes for q in n_states),
        name="R(0)",
    )

    # Restriccion para forzar a rechazar los negativos y aceptar los positivos
    acceptance_pos = (
        n_to_q[n, q] <= is_used[q] for q in n_states for n in tree.f_state_pos()
    )
    acceptance_neg = (
        n_to_q[n, q] <= 1 - is_used[q] for q in n_states for n in tree.f_state_neg()
    )
    model.addConstrs(
        acceptance_pos,
        name="aceptacion pos",
    )
    model.addConstrs(
        acceptance_neg,
        name="aceptacion neg",
    )

    # objective function
    model.setObjective(cost, GRB.MINIMIZE)

    # optimizar
    model.optimize()
    if model.status == GRB.Status.OPTIMAL:
        print("Optimal solution")
        # Acciones para manejar la solución óptima
    elif model.status == GRB.Status.TIME_LIMIT:
        print("Non-optimal solution")
        with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
            file.write("GurobiTimeLimit")
        # Acciones para manejar la solución subóptima
    else:
        print("No solution was found")
    solution = {
        "model": model,
        "n_to_q": n_to_q,
        "delta": delta,
        "cost": cost,
        "is_used": is_used,
        "rev_sigma_dict": rev_sigma_dict,
        "sigma_dict": sigma_dict,
    }
    return solution


if __name__ == "__main__":
    pass
