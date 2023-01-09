import os
import time
import numpy as np
import json
from dags import generate_dag
from traces_ch.trace_generator import generate_trace
from itertools import combinations_with_replacement as combi


def read_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def theformula(nodes: list):
    file_template = ""
    frml_nodes = dict()
    frml_dic = {0: "h({})", 1: "f(op{}, {})", 2: "f(op{}, {}, {})"}
    for i in range(len(nodes)):
        izq, der = nodes[i]
        aux = (np.array(nodes[i]) > 0).sum()
        if aux == 0:
            frml_nodes[f"n{i+1}"] = f"h(pred{i+1})"
            file_template += f"predicate(pred{i+1}).\n"
        elif aux == 1:
            frml_nodes[f"n{i+1}"] = f"f(op{i+1}" + ", {})".format(
                frml_nodes[f"n{der}"]
            )
            file_template += f"unary(op{i+1}).\n"
        elif aux == 2:
            frml_nodes[f"n{i+1}"] = f"f(op{i+1}" + ", {}, {})".format(
                frml_nodes[f"n{izq}"], frml_nodes[f"n{der}"]
            )
            file_template += f"binary(op{i+1}).\n"
    file_template = (
        f"theformula({frml_nodes[f'n{len(nodes)}']})." + "\n" + file_template
    )
    print(file_template)
    return file_template


def traces2formulas(traces_file, n_nodes, tries_limit=500, direct=False):
    valids = []
    if direct:
        lines = traces_file.split("\n")
        lines = [
            line.strip().strip("trace().")
            for line in lines
            if line.strip() != ""
        ]
    else:
        with open(traces_file, "r") as traces:
            lines = traces.readlines()
            lines = [
                line.strip().strip("trace().")
                for line in lines
                if line.strip() != ""
            ]
    preds_allowed = set()
    for line in lines:
        if not (line.startswith("pos") or line.startswith("neg")):
            preds_allowed.add(line.split(",")[1].strip())
    dags_generator = generate_dag(n_nodes, tries_limit)

    for dag_id, dag in dags_generator:
        SATISFIABLE = False
        template_formula = theformula(dag)
        # print(f"Hay {len(preds_allowed)} variables")

        if os.path.exists("solutions.txt"):
            os.remove("solutions.txt")

        with open("theformula.lp", "w") as formula_file:
            formula_file.write(template_formula)

        while not os.path.exists("theformula.lp"):
            time.sleep(0.5)

        start_counter_ns = time.perf_counter_ns()
        os.system(f"clingo theformula.lp main.lp -n 1 > solutions.txt")

        while not os.path.exists("solutions.txt"):
            time.sleep(0.2)

        with open("solutions.txt", "r") as solution_file:
            output = solution_file.readlines()
            if not ("UNSATISFIABLE\n" in output):
                print("SATISFIABLE")
                SATISFIABLE = True
                index_answers = [
                    i + 1
                    for i in range(len(output))
                    if output[i].startswith("Answer")
                ]
                # print(index_answers)
                for j in index_answers:
                    valids.append(output[j])
            else:
                print("UNSATISFIABLE")
        yield SATISFIABLE, dag_id, valids


def run_experiment(max_steps_trace: int, max_len_form: int, direct=False):
    connections = read_json("traces_ch/B6ByNegPMKs_connectivity.json")
    objects = read_json("traces_ch/B6ByNegPMKs_objects.json")
    results = []
    for p in range(4, max_steps_trace + 1):
        trace_sat = False
        total_template = generate_trace(p, connections, objects)
        if not direct:
            with open("traces.lp", "w") as file:
                file.write(total_template)
            while not os.path.exists("traces.lp"):
                time.sleep(0.2)
        traces_file = total_template if direct else "traces.lp"
        for L in range(2, max_len_form + 1):
            print(f"Trying with {p} trace steps and {L} nodes in formula")
            formulas_gen = traces2formulas(traces_file, L, direct=direct)
            start_counter_ns = time.perf_counter_ns()
            for satisfiable, bin_num, valids in formulas_gen:
                if satisfiable:
                    end_counter_ns = time.perf_counter_ns()
                    timer_ns = end_counter_ns - start_counter_ns
                    trace_sat = True
                    results.append((p, L, bin_num, timer_ns / (10**9)))
                    print(results)
                    with open("tiempos.txt", "a") as f:
                        f.write(
                            f"({p}, {L}, {bin_num}, {timer_ns / (10**9)})\n"
                        )
                    break
            if trace_sat:
                print(
                    f"Trace with {p} steps, satisfiable with {L} nodes and structure id {bin_num}"
                )
                break
    return results  # en caso de que llegue hasta el final


###########
if __name__ == "__main__":
    max_steps_trace = 50
    max_len_form = 30
    print("Empiezan experimentos")
    results = run_experiment(max_steps_trace, max_len_form, direct=False)
    print("Terminó experimentos")
    print(results)

    if os.path.exists("solutions.txt"):
        os.remove("solutions.txt")
