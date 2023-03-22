"""
Module with the gurobi-logic
"""

import itertools
from gurobipy import *


class Node(object):
    """
    Node class to codify prefix tree
    """

    new_id = itertools.count()

    def __init__(self, parent_id=None, sigma=None):
        """
        Function
        """
        self.node_id = next(Node.new_id)

        self.parent_id = parent_id
        self.sigma = sigma
        self.sign = None
        self.children = {}


class PrefixTree:
    """
    Prefix Tree that codes the traces. The nodes could be positive, negatives
    or None depending on the sign of the trace.
    """

    def __init__(self, traces, e2b):
        self.ev2binpr = e2b
        self.root = Node()
        self.id_nodes = {0: self.root}
        self.Sigma_simbol = dict()
        self.Sigma = set()
        self.sat = True
        self.process_traces(traces)

    def process_traces(self, traces):
        """
        Function
        """
        for sgn in ["neg", "pos"]:
            for trace in traces[sgn]:
                self.new_trace(trace, sgn)

    def new_trace(self, trace, sign):
        """
        Function
        """
        actual_id = 0
        actual_node = self.id_nodes[actual_id]
        actual_dict = actual_node.children
        for event in trace:
            trace_key = self.ev2binpr(event)  # lo codificamos en sigma
            self.Sigma.add(trace_key)  # agregamos al alfabeto
            self.Sigma_simbol[trace_key] = event
            partial_id = actual_dict.get(trace_key)  # conseguimos nodo

            if partial_id is None:
                new_node = Node(parent_id=actual_node.node_id, sigma=trace_key)
                new_id = new_node.node_id
                self.id_nodes[new_id] = new_node
                actual_dict[trace_key] = new_id

                actual_node = new_node
                actual_dict = actual_node.children
                actual_id = new_id
            else:
                actual_node = self.id_nodes[partial_id]
                actual_dict = actual_node.children
                actual_id = partial_id

        if (actual_node.sign != sign) and (actual_node.sign is not None):
            print("INSATISFIABLE TREE FOR NODE SIGNS")
            print(actual_node.sign, sign)
            node_id = actual_node.node_id
            print(f"Signos no cuadran, camino:{self.find_treepath(node_id)}")
            self.sat = False
        actual_node.sign = sign

    def find_treepath(self, node_id):
        """
        Function
        """
        rev_treepath = []
        rev_treepath.append(node_id)
        node = self.id_nodes[node_id]
        parent_id = node.parent_id
        while parent_id:
            rev_treepath.append(parent_id)
            node = self.id_nodes[parent_id]
            parent_id = node.parent_id
        return list(reversed(rev_treepath))

    def print_tree(self):
        """
        Function
        """

    def parent(self, node_id):
        """
        Function
        """
        return self.id_nodes[node_id].parent_id

    def sigma(self, node_id):
        """
        Function
        """
        return self.id_nodes[node_id].sigma

    def node_sgn(self, node_id):
        """
        Function
        """
        return self.id_nodes[node_id].sign

    def f_state_pos(self):
        """
        Function
        """
        return [id_n for id_n in self.id_nodes if self.node_sgn(id_n) == "pos"]

    def f_state_neg(self):
        """
        Function
        """
        return [id_n for id_n in self.id_nodes if self.node_sgn(id_n) == "neg"]

    def show_signs(self):
        """
        Function
        """
        return {k: v.sign for k, v in self.id_nodes.items()}


class God:
    """
    Function
    """

    def __init__(self, traces):
        predicates = create_preds_vector(traces)
        ev2binpr = event2binpreds(predicates)
        self.arbol = PrefixTree(traces, ev2binpr)

    def give_me_the_plant(self):
        """
        Function
        """
        return self.arbol


class Automata:
    """
    Automata class that encapsulates the information of
    the milp solution
    """

    def __init__(self, delta, is_used, rev_sigma_dict):
        self.delta = delta
        self.is_used = is_used
        self.rev_sigma_dict = rev_sigma_dict
        print("is used", is_used)
        print("rev sigma", rev_sigma_dict)

    def process_trace(self, traces_dict: dict):
        """
        Module that process a trace and return if its a positive, negative or
        unsigned trace
        """
        for sgn, traces in traces_dict.items():
            print(sgn, ":")
            for trace in traces:
                print(trace)


def create_preds_vector(traces):
    """
    Function
    """
    predicates = set()
    for sgn in ["pos", "neg"]:
        for trace in traces[sgn]:
            for event in trace:
                predicates = predicates.union(set(event))
    return tuple(predicates)


def event2binpreds(predicates):
    """
    Function
    """

    def e2b(event):
        return tuple(int(obj in event) for obj in predicates)

    return e2b


def milp(tree, max_states, verbose=0):
    """
    Function
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
    cost = model.addVar(
        vtype=GRB.CONTINUOUS, name="cost"
    )  # funcion de costo auxiliar

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
        n_to_q[n, q] <= is_used[q]
        for q in n_states
        for n in tree.f_state_pos()
    )
    acceptance_neg = (
        n_to_q[n, q] <= 1 - is_used[q]
        for q in n_states
        for n in tree.f_state_neg()
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
    solution = {
        "model": model,
        "n_to_q": n_to_q,
        "delta": delta,
        "cost": cost,
        "is_used": is_used,
        "rev_sigma_dict": rev_sigma_dict,
    }
    return solution


def check_automata(automata, traces) -> bool:
    """
    Function thay checks if an automata accepts and
    rejects the corresponding traces
    """


if __name__ == "__main__":
    from xxtraces_tools import read_json, generate_trace

    p = 2
    connections = read_json("./traces_ch/B6ByNegPMKs_connectivity.json")
    objects = read_json("./traces_ch/B6ByNegPMKs_objects.json")

    all_traces = generate_trace(trace_steps, connections, objects)

    g = God(all_traces)
    arbol = g.give_me_the_plant()
