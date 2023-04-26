"""
General module for experiment related functions
"""

from toro2traces import toro_traces

from xxclingo_main import traces2formulas

from xxgurobi_main import God, milp, Automata
from xxtraces_tools import (
    generate_trace_clingo,
    generate_trace_gurobi,
    pos_negs_traces,
    get_graphs_from_id,
)


def comparing(trace_steps, n_dag_nodes, connections, objects):
    """
    Function
    """
    pos_trace, neg_traces = pos_negs_traces(trace_steps, connections, objects)

    # generate_trace_gurobi(pos_trace, neg_traces, objects)

    traces_template = generate_trace_clingo(pos_trace, neg_traces, objects)
    traces2formulas(traces_template, n_dag_nodes)


def experiment_clingo(room_id: str, trace_steps: int, n_nodes: int):
    """
    Function thats uses clingo to solve the trace-processing problem
    """
    connections, objects = get_graphs_from_id(room_id)
    pos_trace, neg_traces = pos_negs_traces(trace_steps, connections, objects)

    traces_list = generate_trace_gurobi(pos_trace, neg_traces, objects)

    # need fast check
    arbol = God(traces_list).give_me_the_plant()
    if not arbol.sat:
        raise ValueError("UNSATISFIABLE")

    template = generate_trace_clingo(pos_trace, neg_traces, objects)

    is_sat, _, valids = traces2formulas(template, n_nodes)
    return valids if is_sat else list()


def experiment_gurobi(room_id: str, trace_steps: int, max_states: int):
    """
    Function thats uses clingo to solve the trace-processing problem
    """
    connections, objects = get_graphs_from_id(room_id)
    pos_trace, neg_traces = pos_negs_traces(trace_steps, connections, objects)
    traces_list = generate_trace_gurobi(pos_trace, neg_traces, objects)

    # executes milp
    dios = God(traces_list)
    arbol = dios.give_me_the_plant()
    if not arbol.sat:
        raise ValueError("UNSATISFIABLE")

    solution = milp(arbol, max_states)
    automata = Automata(solution)
    automata.set_event2binpreds(dios.ev2binpr)
    automata.set_signs(arbol.f_state_pos(), arbol.f_state_neg())

    if not automata.process_traces(traces_list):
        raise ValueError("Automata is not working properly")

    return automata


def debug_gurobi(max_states: int):
    """
    Function that use the toro traces to debug the system.
    The idea is that the last state transitioned has the same sign as expected
    """
    # Read toro traces
    traces_list = toro_traces()

    # executes milp
    dios = God(traces_list)
    arbol = dios.give_me_the_plant()
    if not arbol.sat:
        raise ValueError("UNSATISFIABLE")
    solution = milp(arbol, max_states)

    automata = Automata(solution)
    automata.set_event2binpreds(dios.ev2binpr)
    automata.set_signs(arbol.f_state_pos(), arbol.f_state_neg())

    if not automata.process_traces(traces_list):
        raise ValueError("Automata is not working properly")

    return automata


if __name__ == "__main__":
    ROOM_ID = "B6ByNegPMKs"
    STEPS = 3

    # MAX_N_DAG_NODES = 4
    # print(experiment_clingo(ROOM_ID, STEPS, MAX_N_DAG_NODES))

    MAX_AUTOMATA_STATES = 10
    print(experiment_gurobi(ROOM_ID, STEPS, MAX_AUTOMATA_STATES))

    # print(debug_gurobi(10))
