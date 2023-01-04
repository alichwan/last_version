import numpy as np
import pandas as pd
import json
import logging
from time import perf_counter
from dags import generate_dag
from automatas_approach.main import God
from automatas_approach.MILP import milp


def read_json(path):
    with open(path, 'r') as json_file:
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

    def generate_trace(self):
        pass

    def trace_to_lp(self, trace):
        pass


class ClingoExperiment:
    def __init__(self, max_dag_nodes, max_dag_tries):
        logging.debug("Initializing ClingoExperiment")
        self.max_dag_nodes = max_dag_nodes
        self.max_dag_tries = max_dag_tries

    def run_experiment(self):
        pass


class GurobiExperiment:
    def __init__(self, max_automata_states):
        logging.debug("Initializing GurobiExperiment")
        self.max_automata_states = max_automata_states

    def gen_tree(self, traces):
        g = God(all_traces)
        self.arbol = g.give_me_the_plant()

    def run_experiment(self):
        pass


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
        # self.gurobi_exp = GurobiExperiment(max_automata_states)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Initial log')
    
    
    exp = Experiment(
        conn_path= './traces_ch/B6ByNegPMKs_connectivity.json',
        objs_path= './traces_ch/B6ByNegPMKs_objects.json',
        min_trace_steps= 3,
        max_trace_steps= 10,
        negative_traces_case= 1,
        max_dag_nodes= 10,
        max_dag_tries= 5000,
        max_automata_states= 10,
    )
