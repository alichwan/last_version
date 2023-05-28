"""
General module for experiment related functions
"""
from time import perf_counter_ns
from toro2traces import toro_traces
from xxclingo_main import traces2formulas
from xxgurobi_main import milp
from god import God
from automata import Automata
from clingo_automata import prefixtree_to_automata
from xxtraces_tools import (
    generate_trace_clingo,
    generate_trace_gurobi,
    pos_negs_traces,
    get_graphs_from_id,
    get_exec_time,
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
        raise ValueError("Unsatisfiable by tree")

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
        raise ValueError("Unsatisfiable by tree")

    solution = milp(arbol, max_states)
    automata = Automata(solution, dios.ev2binpr)
    automata.set_signs(arbol.f_state_pos(), arbol.f_state_neg())

    if not automata.check_traces(traces_list):
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
        raise ValueError("Unsatisfiable by tree")
    solution = milp(arbol, max_states)

    automata = Automata(solution, dios.ev2binpr)
    automata.set_signs(arbol.f_state_pos(), arbol.f_state_neg())

    if not automata.check_traces(traces_list):
        raise ValueError("Automata is not working properly")

    return automata


def debug_csar(max_states: int):
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
        raise ValueError("Unsatisfiable by tree")

    automata = prefixtree_to_automata(arbol, max_states, dios.ev2binpr)
    automata.set_signs(arbol.f_state_pos(), arbol.f_state_neg())

    # automata.plot()
    if not automata.check_traces(traces_list):
        raise ValueError("AutomataClingo is not working properly")

    return automata


@get_exec_time
def time_for_prefixtree_to_csar(arbol, max_states, ev2binpr):
    """Given a prefix tree, this decorated function will return the time in
    seconds that takes to transform the prefix tree into a CSAR, and the
    automaton itself.
    """
    return prefixtree_to_automata(arbol, max_states, ev2binpr)


@get_exec_time
def time_for_prefixtree_to_gsar(arbol, max_states, ev2binpr):
    """Given a prefix tree, this decorated function will return the time in
    seconds that takes to transform the prefix tree into a GSAR, and the
    automaton itself.
    """
    solution = milp(arbol, max_states)
    automata = Automata(solution, ev2binpr)
    return automata


def prefixtree_to_dict(tree):
    """From a PrefixTree class extract the automaton tuple as a dictionary:
    (nodes, states, initial state, final states, transitions)
    """


def csar_to_dict(csar_automaton):
    """From a ClingoAutomata class extract the automaton tuple as a dictionary:
    (nodes, states, initial state, final states, transitions)
    """


def gsar_to_dict(gsar_automaton):
    """From a Automata class extract the automaton tuple as a dictionary:
    (nodes, states, initial state, final states, transitions)
    """


def compare_csar_gsar_debug(max_states: int):
    """
    Function that use the toro traces to debug the system.
    The idea is that the last state transitioned has the same sign as expected
    """
    # Read toro traces
    traces_dict = toro_traces()

    # executes milp
    dios = God(traces_dict)
    arbol = dios.give_me_the_plant()
    if not arbol.sat:
        raise ValueError("Unsatisfiable by tree")

    # CLINGO
    automata_c = prefixtree_to_automata(arbol, max_states, dios.ev2binpr)

    automata_c.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    if not automata_c.check_traces(traces_dict):
        raise ValueError("CSAR Automata has not passed the check")

    # GUROBI
    solution = milp(arbol, max_states)
    automata_g = Automata(solution, dios.ev2binpr)

    automata_g.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    if not automata_g.check_traces(traces_dict):
        raise ValueError("GSAR Automata has not passed the check")

    print(automata_g)

    # CHECKS
    print(automata_c == automata_g)

    print(dios.predicates)
    print(f"Clingo time [s]: {execution_time_c}")
    print(f"Gurobi time [s]: {execution_time_g}")


def compare_csar_gsar_randompaths(max_states: int):
    """Creates random paths to create the positive and negative traces, from
    there a prefix tree will be computed and will passed through clingo solver
    or gurobi solver, check if this solutions are valids and get the time of
    each process.

    Args:
        max_states (int): number of maximum states that can be used to compute
    """


if __name__ == "__main__":
    ROOM_ID = "B6ByNegPMKs"
    STEPS = 3

    # MAX_N_DAG_NODES = 4
    # print(experiment_clingo(ROOM_ID, STEPS, MAX_N_DAG_NODES))

    MAX_AUTOMATA_STATES = 10
    # print(experiment_gurobi(ROOM_ID, STEPS, MAX_AUTOMATA_STATES))
    # print(debug_gurobi(MAX_AUTOMATA_STATES))
    # print(debug_csar(MAX_AUTOMATA_STATES))
    compare_csar_gsar_debug(MAX_AUTOMATA_STATES)
