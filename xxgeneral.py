"""
General module for experiment related functions
"""

import os
from time import sleep, perf_counter_ns
from xxclingo_main import traces2formulas
from xxgurobi_main import God, milp
from xxtraces_tools import read_json, generate_trace


def run_experiment(max_steps_trace: int, max_len_form: int, direct=False):
    """
    Function
    """
    connections = read_json("traces_ch/B6ByNegPMKs_connectivity.json")
    objects = read_json("traces_ch/B6ByNegPMKs_objects.json")
    results = []
    for trace_step in range(4, max_steps_trace + 1):
        trace_sat = False
        total_template = generate_trace(trace_step, connections, objects)
        if not direct:
            with open("traces.lp", "w", encoding="utf-8") as file:
                file.write(total_template)
            while not os.path.exists("traces.lp"):
                sleep(0.2)
        traces_file = total_template if direct else "traces.lp"
        for n_nodes in range(2, max_len_form + 1):
            print(f"Trying with {trace_step} trace steps and {n_nodes} nodes in formula")
            formulas_gen = traces2formulas(traces_file, n_nodes, direct=direct)
            start_counter_ns = perf_counter_ns()
            for satisfiable, bin_num, _ in formulas_gen:
                if satisfiable:
                    end_counter_ns = perf_counter_ns()
                    timer_ns = end_counter_ns - start_counter_ns
                    trace_sat = True
                    results.append((trace_step, n_nodes, bin_num, timer_ns / (10**9)))
                    print(results)
                    with open("tiempos.txt", "a", encoding="utf-8") as f:
                        f.write(
                            f"({trace_step}, {n_nodes}, {bin_num}, {timer_ns / (10**9)})\n"
                        )
                    break
            if trace_sat:
                print(
                    f"Trace with {trace_step} steps, satisfiable with {n_nodes} nodes"
                )
                break
    return results  # en caso de que llegue hasta el final


if __name__ == "__main__":
    pass
