""" Main file considering the traces generated from the kirril
repository. That takes the stamina competition approach.
"""
from typing import Dict
import json
import os
import random
from time import perf_counter_ns
from datetime import datetime
from god import God
from automata import Automata, AutomataKirril
from xxgurobi_main import milp
from clingo_automata import prefixtree_to_automata

# constants
MAX_STATES = 14


def get_kirril_automaton(filename: str):
    """Get the traces from a file in the kirril folder

    Args:
        filename (str): string with the file to be parsed

    Returns:
        BaseAutomaton: Automaton given by the Kirril algorithm
    """
    base_path = "./kirril_files/automatons/"
    transitions = []
    with open(f"{base_path}{filename}", "r", encoding="utf-8") as file:
        for line in file.readlines():
            parsed_line = line.strip().split(" ")
            transitions.append((parsed_line[0], parsed_line[3], parsed_line[5]))
    return AutomataKirril(transitions=transitions)


def get_kirril_traces(filename: str) -> dict:
    """Get the traces from a file in the kirril folder

    Args:
        filename (str): string with the file to be parsed

    Returns:
        dict: traces of the form {'pos': [..], 'neg': [..]}
    """
    base_path = "./kirril_files/traces/"
    try:
        with open(f"{base_path}{filename}", "r", encoding="utf-8") as file:
            traces = json.load(file)
        return traces
    except Exception as e:
        print(f"Error loading json: {filename}")
        print(e)


def split_traces(traces: Dict[str, list], train_frac: float):
    """Function that takes a dict of traces positives and negatives and splits
    them into train and test sets

    Args:
        traces (Dict[str, list]): Set of all traces
        train_frac (float): Fraction of traces that will be considered for the
            training set. Must be between 0 and 1.
    """
    train_sample_size = {
        "pos": int(len(traces["pos"]) * train_frac),
        "neg": int(len(traces["neg"]) * train_frac),
    }

    train_set = {}
    test_set = {}

    for sign in ["pos", "neg"]:
        aux_list = traces[sign]
        random.shuffle(aux_list)
        print(aux_list)

        train_set[sign] = aux_list[: train_sample_size[sign]]
        test_set[sign] = aux_list[train_sample_size[sign] :]
    return train_set, test_set


def csar_from_traces(traces: Dict[str, list]):
    """Calculates the CSAR for training traces.
    Side effect: Writes in logs the time and size of the automaton.

    Raise:
        ValueError: if predix tree is not satisfiable.
    """
    dios = God(traces)
    arbol = dios.give_me_the_plant()
    if not arbol.sat:
        raise ValueError("Unsatisfiable by tree")

    automata = prefixtree_to_automata(arbol, MAX_STATES, dios.ev2binpr)
    automata.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    return automata


def gsar_from_traces(traces: Dict[str, list]):
    """Calculates the GSAR for training traces.
    Side effect: Writes in logs the time and size of the automaton.

    Raise:
        ValueError: if predix tree is not satisfiable.
    """
    dios = God(traces)
    arbol = dios.give_me_the_plant()
    if not arbol.sat:
        raise ValueError("Unsatisfiable by tree")

    time_start = perf_counter_ns()
    solution = milp(arbol, MAX_STATES)
    time_end = perf_counter_ns()
    with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
        file.write(f"Gurobi_time: {( time_end - time_start ) / ( 10**9 )}\n")
    automata = Automata(solution, dios.ev2binpr)
    automata.set_signs(arbol.f_state_pos(), arbol.f_state_neg())
    return automata


def automaton_is_correct(automaton, traces: Dict[str, list]) -> bool:
    """Checker of correctness of an automaton

    Args:
        automaton (Union[AutomataBase, AutomataKirril]): instance to check
        traces (Dict[str, list]): traces of training, {'pos': [...], 'neg': [...]}

    Returns:
        bool: true if the automaton can be considered as valid.
    """
    for sgn, traces in traces.items():
        for trace in traces:
            automaton_sign_guess = automaton.process_just_one_trace(trace)
            if automaton_sign_guess != sgn:
                return False
    return True


def run_configuration(configuration: Dict[str, int]):
    """Experinment that runs the configuration.
    Args:
        name (str): String that describes the configuration
        configuration (Tuple[int, int, int, int, int]): tuple with the params.
    """
    states = configuration["s"]
    language = configuration["l"]
    counter = configuration["c"]
    tracespersign = configuration["t"]
    extrapath = configuration["x"]
    problem_name = f"{states}S_{language}L_{counter}C_{tracespersign}T_{extrapath}X"
    if not os.path.exists(f"./kirril_files/original_files/{problem_name}.txt"):
        print("Trace doesn't exist")
        return None

    with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
        file.write(f"Problem_id: {problem_name}\n")

    # goes to read the kirril automaton
    # instantiate that automaton
    # [Not needed for change in the approach]
    # kirril_automaton = get_kirril_automaton(f"{problem_name}.txt")

    # goes to read the traces of kirril
    # {'pos':[...],'neg':[...]}
    traces = get_kirril_traces(f"{problem_name}.json")

    # [CANCELLED]: split into train and test traces
    # train_traces, test_traces = split_traces(traces, train_frac=0.7)

    # run CSAR solution and get time and size of excecution
    csar = csar_from_traces(traces)
    len_csar = len(csar)

    # run GSAR solution and get time and size of excecution
    gsar = gsar_from_traces(traces)
    len_gsar = len(gsar)

    # Write lengths of automatons
    with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
        file.write(f"Clingo_size: {len_csar}\n")
        file.write(f"Gurobi_size: {len_gsar}\n\n")

    # Not needed for this approach
    # masked_traces = [steps for t in traces.values() for steps in t]

    # take each solution and the kirril automaton and process the test traces
    # kirril_automaton.compare
    if not automaton_is_correct(csar, traces):
        with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
            file.write(
                "Last experiment not valid because of incorrectness of clingo automata\n"
            )
        raise ValueError("clingo automaton not correct")

    if not automaton_is_correct(gsar, traces):
        with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
            file.write(
                "Last experiment not valid because of incorrectness of gurobi automata\n"
            )
        raise ValueError("gurobi automaton not correct")


def main():
    """Encapsulated main function"""
    if os.path.exists("./curr_experiment.txt"):
        os.remove("./curr_experiment.txt")
    # define configuration o the problems
    # this is number of states, size of the alphabet,
    # random seed id, number of traces for sign and
    # extra traces length.
    configurations = [
        {"s": 50, "l": l, "c": 0, "t": t, "x": x}
        for x in [0, 10, 50]
        for t in [5, 10, 15, 50]
        for l in [5, 10, 20, 50]
    ]

    # for loop for each configuration
    with open("./curr_experiment.txt", "a", encoding="utf-8") as file:
        file.write(f"EXPERIMENTS max_states = {MAX_STATES}\n\n")
    for configuration in configurations:
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f")
        print(f"Running {configuration} at {time}")
        run_configuration(configuration)


# others
if __name__ == "__main__":
    main()
