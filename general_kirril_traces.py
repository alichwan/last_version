"""
General module for experiment related functions
"""
from typing import Any
import pandas as pd
from toro2traces import toro_traces
from kirril2traces import get_kirril_traces
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
    objects_to_str,
)
from graph import Graph


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


def gen_template_clingo_kirril(traces: dict):
    """
    Function
    """
    total_template = ""
    counter_id = 0
    for pos_trace in traces["pos"]:
        counter_id += 1
        total_template += objects_to_str(pos_trace, counter_id, "pos")
    for neg_trace in traces["neg"]:
        counter_id += 1
        total_template += objects_to_str(neg_trace, counter_id, "neg")
    return total_template.strip()


def experiment_clingo_kirril(n_nodes: int):
    """
    Function thats uses clingo to solve the trace-processing problem
    """
    # traces_list = get_kirril_traces("50S10L0C.json")
    traces_list = get_kirril_traces("6S5L0C.json")

    # need fast check
    arbol = God(traces_list).give_me_the_plant()
    if not arbol.sat:
        raise ValueError("Unsatisfiable by tree")

    template = gen_template_clingo_kirril(traces_list)

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
def time_for_prefixtree_to_csar(arbol, max_states, ev2binpr) -> [float, Any]:
    """Given a prefix tree, this decorated function will return the time in
    seconds that takes to transform the prefix tree into a CSAR, and the
    automaton itself.

    returns:
        - excecution_time (float): Time in seconds that takes the function
        - automaton (AutomataClingo): The automaton returned
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
    time_c, automata_c = time_for_prefixtree_to_csar(
        arbol, max_states, dios.ev2binpr
    )

    automata_c.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    if not automata_c.check_traces(traces_dict):
        raise ValueError("CSAR Automata has not passed the check")

    # GUROBI
    time_g, automata_g = time_for_prefixtree_to_gsar(
        arbol, max_states, dios.ev2binpr
    )

    automata_g.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    if not automata_g.check_traces(traces_dict):
        raise ValueError("GSAR Automata has not passed the check")

    print(automata_g)

    # CHECKS
    print(automata_c == automata_g)

    print(dios.predicates)
    print(f"Clingo time [s]: {time_c}")
    print(f"Gurobi time [s]: {time_g}")


def compare_csar_debug(max_states: int):
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
    time_c, automata_c = time_for_prefixtree_to_csar(
        arbol, max_states, dios.ev2binpr
    )

    automata_c.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    if not automata_c.check_traces(traces_dict):
        raise ValueError("CSAR Automata has not passed the check")

    # GUROBI
    time_g, automata_g = time_for_prefixtree_to_gsar(
        arbol, max_states, dios.ev2binpr
    )

    automata_g.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    if not automata_g.check_traces(traces_dict):
        raise ValueError("GSAR Automata has not passed the check")

    print(automata_g)

    # CHECKS
    print(automata_c == automata_g)

    print(dios.predicates)
    print(f"Clingo time [s]: {time_c}")
    print(f"Gurobi time [s]: {time_g}")


def compare_csar_gsar_randompaths(
    room_id: str, min_steps: int = 3, max_steps: int = 5, max_states: int = 10
):
    """Creates random paths to create the positive and negative traces, from
    there a prefix tree will be computed and will passed through clingo solver
    or gurobi solver, check if this solutions are valids and get the time of
    each process.

    Args:
        room_id (str): ID of the graph that would be used to get the objects
        min_steps (int, optional): Length of the shortest trace to evaluate. Defaults to 3.
        max_steps (int, optional): Length of the larges trace to evaluate. Defaults to 5.
        max_states (int, optional): Max states that can have the solution. Defaults to 10.
    """
    # list to store
    nsteps = []
    pt2csar_time = []
    pt2gsar_time = []
    csar_states = []
    gsar_states = []

    base_graph = Graph(
        f"traces_ch/{room_id}_connectivity.json",
        f"traces_ch/{room_id}_objects.json",
    )

    for n_steps in range(min_steps, max_steps + 1):
        # generate random traces with incremental number of steps
        traces_dict = base_graph.generate_traces(n_steps)
        print(traces_dict["pos"])
        # get the traces and embed the automatas
        god = God(traces_dict)
        tree = god.give_me_the_plant()
        if not tree.sat:
            # raise ValueError("Unsatisfiable by tree")
            continue

        # CLINGO
        time_c, automata_c = time_for_prefixtree_to_csar(
            tree, max_states, god.ev2binpr
        )
        automata_c.set_signs(tree.f_state_pos(), tree.f_state_neg())
        if not automata_c.check_traces(traces_dict):
            # raise ValueError("CSAR Automata has not passed the check")
            # csar_states.append("Error")
            continue

        # GUROBI
        time_g, automata_g = time_for_prefixtree_to_gsar(
            tree, max_states, god.ev2binpr
        )
        automata_g.set_signs(tree.f_state_pos(), tree.f_state_neg())
        if not automata_g.check_traces(traces_dict):
            # raise ValueError("GSAR Automata has not passed the check")
            # gsar_states.append("Error")
            continue

        nsteps.append(n_steps)
        csar_states.append(len(automata_c.state_signs))
        gsar_states.append(len(automata_g.state_signs))

        pt2csar_time.append(time_c)
        pt2gsar_time.append(time_g)
        del traces_dict
        del god
        del tree

    final_data = {
        "n steps": nsteps,
        "csar time": pt2csar_time,
        "gsar_time": pt2gsar_time,
        "n csar states": csar_states,
        "n gsar states": gsar_states,
    }
    return pd.DataFrame(final_data)


def compare_csar_randompaths(
    room_id: str, min_steps: int = 3, max_steps: int = 5, max_states: int = 10
):
    """Creates random paths to create the positive and negative traces, from
    there a prefix tree will be computed and will passed through clingo solver
    or gurobi solver, check if this solutions are valids and get the time of
    each process.

    Args:
        room_id (str): ID of the graph that would be used to get the objects
        min_steps (int, optional): Length of the shortest trace to evaluate. Defaults to 3.
        max_steps (int, optional): Length of the larges trace to evaluate. Defaults to 5.
        max_states (int, optional): Max states that can have the solution. Defaults to 10.
    """
    # list to store
    nsteps = []
    pt2csar_time = []
    csar_states = []

    base_graph = Graph(
        f"traces_ch/{room_id}_connectivity.json",
        f"traces_ch/{room_id}_objects.json",
    )

    for n_steps in range(min_steps, max_steps + 1):
        # generate random traces with incremental number of steps
        traces_dict = base_graph.generate_traces(n_steps)
        print(traces_dict["pos"])
        # get the traces and embed the automatas
        god = God(traces_dict)
        tree = god.give_me_the_plant()
        if not tree.sat:
            # raise ValueError("Unsatisfiable by tree")
            continue

        # CLINGO
        time_c, automata_c = time_for_prefixtree_to_csar(
            tree, max_states, god.ev2binpr
        )
        automata_c.set_signs(tree.f_state_pos(), tree.f_state_neg())
        if not automata_c.check_traces(traces_dict):
            # raise ValueError("CSAR Automata has not passed the check")
            # csar_states.append("Error")
            continue

        nsteps.append(n_steps)
        csar_states.append(len(automata_c.state_signs))

        pt2csar_time.append(time_c)
        del traces_dict
        del god
        del tree

    final_data = {
        "n steps": nsteps,
        "csar time": pt2csar_time,
        "n csar states": csar_states,
    }
    return pd.DataFrame(final_data)


if __name__ == "__main__":
    MAX_N_DAG_NODES = 7
    MAX_STATES = 10

    print(experiment_clingo_kirril(MAX_N_DAG_NODES))

    # print(experiment_gurobi(ROOM_ID, STEPS, MAX_STATES))
    # print(debug_gurobi(MAX_STATES))
    # print(debug_csar(MAX_STATES))
    # compare_csar_gsar_debug(MAX_STATES)

    # csar_vs_gsar_times = get_exec_time(compare_csar_randompaths)
    # time_total, df_results = csar_vs_gsar_times(ROOM_ID, 20, 50, MAX_STATES)
    # print("Total time: ", time_total)
    # print(df_results)
    # df_results.to_csv("experiments_csar_gsar.csv")

    # last_node_mode_csar_gsar(ROOM_ID, MAX_STATES, STEPS)
    # print(compare_csar_gsar_last_node_mode(ROOM_ID, 31, 40, MAX_STATES))
