"""
Module with the clingo-logic
"""

import os
import numpy as np
from dags import generate_dag
from xxtraces_tools import generate_trace_clingo


def theformula(nodes: list):
    """
    Function
    """
    file_template = ""
    formula_nodes = dict()
    for i, dag in enumerate(nodes):
        izq, der = dag
        degree = (np.array(dag) > 0).sum()
        if degree == 0:
            formula_nodes[f"n{i+1}"] = f"h(pred{i+1})"
            file_template += f"predicate(pred{i+1}).\n"
        elif degree == 1:
            arg = formula_nodes[f"n{der}"]
            formula_nodes[f"n{i+1}"] = f"f(op{i+1}, {arg})"
            file_template += f"unary(op{i+1}).\n"
        elif degree == 2:
            l_arg, r_arg = formula_nodes[f"n{izq}"], formula_nodes[f"n{der}"]
            formula_nodes[f"n{i+1}"] = f"f(op{i+1}, {l_arg}, {r_arg})"
            file_template += f"binary(op{i+1}).\n"
    formulae = formula_nodes[f"n{len(nodes)}"]
    file_template = f"theformula({formulae}).\n{file_template}"
    return file_template


def check_sat(valids) -> (bool, list):
    """
    Function to check if a solution file from clingo program is satisfiable
    """
    with open("solutions.txt", "r", encoding="utf-8") as solution_file:
        output = solution_file.readlines()

    if not "UNSATISFIABLE\n" in output:
        print("SATISFIABLE")
        index_answers = [
            idx + 1
            for idx, line in enumerate(output)
            if line.startswith("Answer")
        ]
        for j in index_answers:
            valids.append(output[j])
        return True, valids
    print("UNSATISFIABLE")
    return False, valids


def traces_to_file(trace_steps: int, connections: dict, objects: dict) -> None:
    """
    Function that given traces write a file to be processed by clingo
    """
    total_template = generate_trace_clingo(trace_steps, connections, objects)
    with open("traces.lp", "w", encoding="utf-8") as file:
        file.write(total_template)


def formula_to_file(template_formula: str):
    """
    Function that given a formula write a file to be processed by clingo
    """
    with open("theformula.lp", "w", encoding="utf-8") as formula_file:
        formula_file.write(template_formula)


def traces2formulas(
    n_dag_nodes: int,
    trace_steps: int,
    connections: dict,
    objects: dict,
    tries_limit=500,
):
    """
    Main function
    """
    dags_generator = generate_dag(n_dag_nodes, tries_limit)
    traces_to_file(trace_steps, connections, objects)

    valids = []
    for dag_id, dag in dags_generator:
        template_formula = theformula(dag)
        formula_to_file(template_formula)

        if os.path.exists("solutions.txt"):
            os.remove("solutions.txt")

        os.system("clingo theformula.lp main.lp -n 1 > solutions.txt")
        # while not os.path.exists("solutions.txt"):
        #     time.sleep(0.2)
        satisfiable, valids = check_sat(valids)
        yield satisfiable, dag_id, valids


if __name__ == "__main__":
    pass
