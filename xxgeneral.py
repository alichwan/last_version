"""
General module for experiment related functions
"""

from time import perf_counter_ns
from xxclingo_main import traces2formulas
from xxgurobi_main import God, milp, Automata
from xxtraces_tools import (
    read_json,
    generate_trace_clingo,
    generate_trace_gurobi,
    pos_negs_traces,
    get_graphs_from_id,
)


# def run_experiment(max_steps_trace: int, max_len_form: int):
#     """
#     Function
#     """
#     connections = read_json("traces_ch/B6ByNegPMKs_connectivity.json")
#     objects = read_json("traces_ch/B6ByNegPMKs_objects.json")
#     results = []
#     for trace_steps in range(4, max_steps_trace + 1):
#         trace_sat = False
#         for n_nodes in range(2, max_len_form + 1):
#             print(
#                 f"Trying with {trace_steps} trace steps and {n_nodes} nodes in formula"
#             )
#             formulas_gen = traces2formulas(
#                 n_nodes, trace_steps, connections, objects
#             )
#             start_counter_ns = perf_counter_ns()
#             for satisfiable, bin_num, _ in formulas_gen:
#                 if satisfiable:
#                     end_counter_ns = perf_counter_ns()
#                     timer_ns = end_counter_ns - start_counter_ns
#                     trace_sat = True
#                     results.append(
#                         (trace_steps, n_nodes, bin_num, timer_ns / (10**9))
#                     )
#                     print(results)
#                     with open("tiempos.txt", "a", encoding="utf-8") as file:
#                         file.write(
#                             f"({trace_steps}, {n_nodes}, {bin_num}, {timer_ns / (10**9)})\n"
#                         )
#                     break
#             if trace_sat:
#                 print(
#                     f"Trace with {trace_steps} steps, satisfiable with {n_nodes} nodes"
#                 )
#                 break
#     return results  # en caso de que llegue hasta el final


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
    arbol = God(traces_list).give_me_the_plant()
    if not arbol.sat:
        raise ValueError("UNSATISFIABLE")
    sol = milp(arbol, max_states)
    automata = Automata(sol["delta"], sol["is_used"], sol["rev_sigma_dict"])
    # if automata.process_trace(traces_list): good
    return automata


if __name__ == "__main__":
    ROOM_ID = "B6ByNegPMKs"
    STEPS = 3

    # MAX_AUTOMATA_STATES = 10
    # print(experiment_gurobi(ROOM_ID, STEPS, MAX_AUTOMATA_STATES))

    MAX_N_DAG_NODES = 4
    print(experiment_clingo(ROOM_ID, STEPS, MAX_N_DAG_NODES))
