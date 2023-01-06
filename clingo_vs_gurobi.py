import numpy as np
import pandas as pd
import json
import logging
from time import perf_counter
from dags import generate_dag
from automatas_approach.main import God
from automatas_approach.MILP import milp


def read_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


class Graph:
    def __init__(
        self,
        connections_path: str,
        objects_path: str,
        negative_traces_case: int,
    ):
        self.connections = read_json(connections_path)
        self.objects = read_json(objects_path)
        self.negative_traces_case = negative_traces_case

    def generate_traces(self, n_steps: int):
        ...

    def traces_to_lp(self, traces):
        ...


class ClingoExperiment:
    def __init__(self, max_dag_nodes, max_dag_tries):
        logging.debug("Initializing ClingoExperiment")
        self.max_dag_nodes = max_dag_nodes
        self.max_dag_tries = max_dag_tries

    def run(self, traces):
        # invoke the clingo solver from ./main.py
        ...


class GurobiExperiment:
    def __init__(self, max_automata_states):
        logging.debug("Initializing GurobiExperiment")
        self.max_automata_states = max_automata_states

    def gen_tree(self, traces):
        g = God(all_traces)
        self.arbol = g.give_me_the_plant()

    def run(self, traces):
        # invoke the gurobi solver from milp
        ...


class Experiment:
    def __init__(
        self,
        conn_path: str,
        objs_path: str,
        min_trace_steps=2,
        max_trace_steps=4,
        negative_traces_case=1,
        max_dag_nodes=4,
        max_dag_tries=200,
        max_automata_states=10,
    ):
        self.min_trace_steps = min_trace_steps
        self.max_trace_steps = max_trace_steps

        self.graph = Graph(conn_path, objs_path, negative_traces_case)
        self.clingo_exp = ClingoExperiment(max_dag_nodes, max_dag_tries)
        self.gurobi_exp = GurobiExperiment(max_automata_states)

    def run(self):
        cli_times = []
        gur_times = []
        steps_range = range(self.min_trace_steps, self.max_trace_steps + 1)
        for n_steps in steps_range:
            traces_cli = self.graph.generate_traces(n_steps)  # TODO
            traces_gur = self.graph.traces_to_lp(traces_cli)

            time_cli_start = perf_counter()
            self.clingo_exp.run(traces_cli)  # TODO
            time_cli_end = perf_counter()

            time_gur_start = perf_counter()
            self.gurobi_exp.run(traces_gur)  # TODO
            time_gur_end = perf_counter()

            cli_times.append(time_cli_start - time_cli_end)
            gur_times.append(time_gur_start - time_gur_end)

        data = {"clng": cli_times, "grb": gur_times}
        return pd.DataFrame(data, index=steps_range)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Initial log")

    exp = Experiment(
        conn_path="./traces_ch/B6ByNegPMKs_connectivity.json",
        objs_path="./traces_ch/B6ByNegPMKs_objects.json",
        min_trace_steps=3,
        max_trace_steps=10,
        negative_traces_case=1,
        max_dag_nodes=10,
        max_dag_tries=5000,
        max_automata_states=10,
    )
    results = exp.run()
    print(results)
