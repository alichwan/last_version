"""clingo_automata
Get an AutomataClingo from a PrefixTree instance

Memo for ME, the module just converts a PT to a AutomataClingo, try not to put all
the data flow here
"""
# imports
import os
from typing import Callable
from prefixtree import PrefixTree
from automata import AutomataClingo
from time import perf_counter_ns

# constants
TREE_LP_FILE = "prefix_tree.lp"


# functions
def extract_solution(solution: str):
    """Extracts the important part of a clingo output for the automata proeblem

    Args:
        solution (str): Console output from clingo
    """
    solution_lines = solution.split()
    # if optimized=YES
    print(solution_lines)


def embed_automata(parsed_sol: str, e2b: Callable) -> AutomataClingo:
    """
    Encapsulates the optimal solution of the clingo solver in AutomataClingo class
    """
    splitted_sol = parsed_sol.strip().split(" ")
    delta = []
    n_to_q = []
    sigma = []
    q_signs = {}
    for element in splitted_sol:
        if element.startswith("delta"):
            delta.append(element.strip("delta()").split(","))
        elif element.startswith("mapping"):
            n_to_q.append(element.strip("mapping()").split(","))
        elif element.startswith("sigma"):
            sigma.append(element.strip('sigma("")'))
        elif element.startswith("final"):
            sgn_q = element.strip("final")
            if sgn_q.startswith("Pos"):
                pos_q = sgn_q.strip("Pos()")
                q_signs[int(pos_q)] = "pos"
            elif sgn_q.startswith("Neg"):
                neg_q = sgn_q.strip("Neg()")
                q_signs[int(neg_q)] = "neg"
            else:
                raise ValueError("Final state without sign")
        else:
            raise ValueError("Unknown element in output from Clingo solver")

    solution = {
        "delta": delta,
        "n_to_q": n_to_q,
        "ssigma": sigma,
        "states_signs": q_signs,
    }
    return AutomataClingo(solution, e2b)


def clean_an_check_csar(clingo_sol: list[str]) -> str:
    """Clean the original solution given by clingo and checks if the solution
    is satisfiable and optimal

    Args:
        clingo_sol (str): Original output captures from clingo excecution

    Returns:
        str: if satisfiable and optimal, the parsed solution
    """

    if "UNSATISFIABLE\n" in clingo_sol:
        raise ValueError("Unsatisfiable solution: detected in parsing")

    optimal_index = clingo_sol.index("OPTIMUM FOUND\n")
    # raise a ValueError if optimal not found
    optimal_answer_index = optimal_index - 2
    return clingo_sol[optimal_answer_index]


def clingo_io(tree_str: str, fpath: str, max_q: int) -> str:
    """makes the input/output work in the flow

    Args:
        tree_str (str): encoded prefix tree in clingo format
        fpath (str): path where the tree should be written

    Returns:
        str: the solution text given by clingo
    """
    with open(fpath, "w", encoding="UTF-8") as file:
        file.write(tree_str)

    # this part can be adapted to inpython clingo
    # fpath is the name of the file that saves the prefixtree in clingo
    time_start = perf_counter_ns()
    os.system(f"clingo {fpath} map_automata_b2.lp -c maxStates={max_q} > CSAR.txt")
    time_end = perf_counter_ns()
    # sleep(2)
    with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
        file.write(f"Clingo_time: {( time_end - time_start ) / ( 10**9 )}\n")
    with open("CSAR.txt", "r", encoding="UTF-8") as solution:
        solution_text = solution.readlines()
    return solution_text


def prefixtree_to_automata(
    tree: PrefixTree, max_states: int, e2b: Callable
) -> AutomataClingo:
    """Function that transforms the tree into a clingo code, executes it
    and extracts the final automata if exists. Then this automata is
    embedded into the AutomataClingo class

    Args:
        tree (PrefixTree): Prefix tree to be transformed, must have the
        ´to_asp´ method.

    Returns:
        AutomataClingo: instance of AutomataClingo class
    """
    asp_tree = tree.to_asp()
    clingo_output = clingo_io(asp_tree, TREE_LP_FILE, max_states)
    csar_checked = clean_an_check_csar(clingo_output)
    automata = embed_automata(csar_checked, e2b)
    return automata


def main():
    """
    Main function to test functionality
    """


if __name__ == "__main__":
    main()
