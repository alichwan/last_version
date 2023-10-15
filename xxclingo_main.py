"""
Module with the clingo-logic
"""

import os
from time import sleep
import numpy as np
from dags import generate_dag
from xxtraces_tools import generate_trace_clingo


def theformula(nodes: list) -> str:
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

    if "SATISFIABLE\n" in output:
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
    print(output)
    return False, valids


def traces_to_file(traces_template: str) -> None:
    """
    Function that writes a lp file with traces to be processed by clingo
    """
    with open("traces.lp", "w", encoding="utf-8") as file:
        file.write(traces_template)


def formula_to_file(template_formula: str):
    """
    Function that writes a lp file with the formula to be processed by clingo
    """
    with open("theformula.lp", "w", encoding="utf-8") as formula_file:
        formula_file.write(template_formula)


def traces2formulas(
    traces_template: str,
    max_n_dag_nodes: int,
    tries_limit=50,
):
    """
    Main function
    Input:
        max_n_dag_nodes: max number of predicates that should have the formula
        trace_steps: number of steps that the random walk should have

    """
    for n_dag_nodes in range(2, max_n_dag_nodes + 1):
        print(f"VUELTA {n_dag_nodes}")
        dags_generator = generate_dag(n_dag_nodes, tries_limit)

        traces_to_file(traces_template)

        valids = []
        for dag_id, dag in dags_generator:
            print(f"Iterating dags, actual id: {dag_id}")
            template_formula = theformula(dag)
            formula_to_file(template_formula)
            sleep(0.2)

            if os.path.exists("solutions.txt"):
                os.remove("solutions.txt")
            os.system("clingo theformula.lp main.lp -n 1 > solutions.txt")
            while not os.path.exists("solutions.txt"):
                sleep(0.2)
            satisfiable, valids = check_sat(valids)
            if satisfiable:
                os.remove("solutions.txt")
                print(template_formula)
                return True, dag_id, valids
        os.remove("solutions.txt")
    # TODO
    print("REMEMBER TO FIX CLINGO WAY")
    return False, -1, []


if __name__ == "__main__":
    pass
