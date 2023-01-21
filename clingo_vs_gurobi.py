import os
import numpy as np
import pandas as pd
import json
import logging
from time import perf_counter, sleep
from automatas_approach.main import God
from automatas_approach.MILP import milp
from main import traces2formulas
from traces_ch.trace_generator import (
    check_trace,
    alternative_traces,
    traces_to_objects,
    gen_traces_file,
    objects_to_str
)


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

    def random_walk(self, start: str, steps: int):
        pos_trace = []
        alternatives = []
        actual = start
        pos_trace.append(actual)
        for step in range(steps):
            options = self.connections[actual]
            if not options:
                raise ValueError("No hay opciones para caminar")
            actual = np.random.choice(options)
            pos_trace.append(actual)
            if self.negative_traces_case >= 1:
                alternatives.append([op for op in options if op != actual])
        if self.negative_traces_case >= 2:
            for i in range(1, len(pos_trace)):
                alternatives.append(pos_trace[:i])
        return pos_trace, alternatives

    def generate_traces(self, n_steps: int):
        start = np.random.choice([*self.connections.keys()])
        while 1:
            logging.debug("generating some valid trace")
            pos_trace, alternatives = self.random_walk(start, n_steps)
            if check_trace(pos_trace, self.objects):
                break
        neg_traces = alternative_traces(pos_trace, alternatives)
        return pos_trace, neg_traces

    def traces_to_objects_dict(self, pos_traces, neg_traces):
        pos_objects = [
            traces_to_objects(tr, self.objects) for tr in pos_traces
        ]
        neg_objects = [
            traces_to_objects(tr, self.objects) for tr in neg_traces
        ]
        return {
            "pos": pos_objects,
            "neg": neg_objects,
        }

    def traces_to_lp(self, pos_trace, neg_traces):
        total_template = gen_traces_file(pos_trace, neg_traces, self.objects)
        return total_template


class ClingoExperiment:
    def __init__(self, max_dag_nodes, max_dag_tries):
        logging.debug("Initializing ClingoExperiment")
        self.max_dag_nodes = max_dag_nodes
        self.max_dag_tries = max_dag_tries

    def solve(self, traces_str):
        logging.debug("Running Clingo")
        with open("traces.lp", "w") as file:
            file.write(traces_str)
        while not os.path.exists("traces.lp"):
            sleep(0.2)
        for n_nodes in range(2, self.max_dag_nodes + 1):
            print(f"Trying {n_nodes} nodes in formula")
            formulas_gen = traces2formulas(
                "traces.lp",
                n_nodes,
                tries_limit=self.max_dag_tries
            )
            for satisfiable, dag_id, valids in formulas_gen:
                if satisfiable:
                    with open("solutions.txt", "r") as solution_file:
                        return solution_file.readlines()
        return "UNSAT"

    def run(self, traces_str):
        logging.debug("Running Clingo")
        with open("traces.lp", "w") as file:
            file.write(traces_str)
        while not os.path.exists("traces.lp"):
            sleep(0.2)
        for n_nodes in range(2, self.max_dag_nodes + 1):
            print(f"Trying {n_nodes} nodes in formula")
            formulas_gen = traces2formulas(
                "traces.lp",
                n_nodes,
                tries_limit=self.max_dag_tries
            )
            for satisfiable, dag_id, valids in formulas_gen:
                if satisfiable:
                    return "SAT"
        return "UNSAT"


class GurobiExperiment:
    def __init__(self, max_automata_states):
        logging.debug("Initializing GurobiExperiment")
        self.max_automata_states = max_automata_states

    def solve(self, traces):
        logging.debug("Running Gurobi")
        logging.debug("Creando a Dios")
        g = God(traces)
        logging.debug("Generando arbol")
        arbol = g.give_me_the_plant()

        if not arbol.sat:
            return "UNSAT"

        assert arbol.id_nodes[0]._id == 0
        logging.debug("Arbol satisfacible")
        modelo, x, delta, c, f, rev_Sigma_dict = milp(arbol, 5, 0)
        logging.debug("Resolvio el MILP")

        if modelo.Status == 2:
            # ver resultados
            res = ""
            for i in x :
                if x[i].X > 0.2:
                    res += f"{(i, x[i].X)}\n"
            for q,s,qp in delta:
                if q != qp and delta[q,s,qp].X > 0.2:
                    res += f"({q},{s},{qp}), {delta[q,s,qp].X}\n"
            arbol.print_tree()
            print(arbol.sat)
            print(arbol.Sigma)
            print(arbol.id_nodes)
            print(arbol.show_signs())
            return res
        elif modelo.Status == 3:
            print("Modelo insatisfacible, ID de status:", modelo.Status)
            return "UNSAT"
        else:
            raise ValueError("Status of MILP model get id: ", modelo.Status)

    def run(self, traces):
        logging.debug("Running Gurobi")
        logging.debug("Creando a Dios")
        g = God(traces)
        logging.debug("Generando arbol")
        arbol = g.give_me_the_plant()

        if not arbol.sat:
            return "UNSAT"

        assert arbol.id_nodes[0]._id == 0
        logging.debug("Arbol satisfacible")
        modelo, x, delta, c, f, rev_Sigma_dict = milp(arbol, 5, 0)
        logging.debug("Resolvio el MILP")

        if modelo.Status == 2:
            # ver resultados
            # for i in x :
            #     if x[i].X > 0.2:
            #         print(i, x[i].X)
            # for q,s,qp in delta:
            #     if q != qp and delta[q,s,qp].X > 0.2:
            #         print(f"({q},{s},{qp}), {delta[q,s,qp].X}")
            return "SAT"
        elif modelo.Status == 3:
            print("Modelo insatisfacible, ID de status:", modelo.Status)
            return "UNSAT"
        else:
            raise ValueError("Status of MILP model get id: ", modelo.Status)


class Experiment:
    def __init__(
        self,
        conn_path: str,
        objs_path: str,
        min_trace_steps=2,
        max_trace_steps=4,
        negative_traces_case=2,
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
            pos_t, neg_ts = self.graph.generate_traces(n_steps)
            pos_ts = [
                pos_t,
            ]
            traces_gur = self.graph.traces_to_objects_dict(pos_ts, neg_ts)
            traces_cli = self.graph.traces_to_lp(pos_t, neg_ts)

            time_cli_start = perf_counter()
            self.clingo_exp.run(traces_cli)
            time_cli_end = perf_counter()

            time_gur_start = perf_counter()
            self.gurobi_exp.run(traces_gur)
            time_gur_end = perf_counter()

            cli_times.append(time_cli_end - time_cli_start)
            gur_times.append(time_gur_end - time_gur_start)

        data = {
            "Traces steps": steps_range,
            "Clingo time[s]": cli_times,
            "Gurobi time[s]": gur_times,
        }
        df_results = pd.DataFrame(data)
        difference = (
            df_results["Clingo time[s]"] - df_results["Gurobi time[s]"]
        )
        df_results["faster"] = difference.map(
            lambda x: "Gurobi" if x < 0 else "Clingo"
        )
        df_results["difference [s]"] = abs(difference)
        return df_results

    def traces_to_lp_local(self, pos_traces, neg_traces):
        """
        Here is broken the abstraction for a specific case
        """
        total_template = ""
        counter_id = 0
        for pos_trace in pos_traces:
            counter_id += 1
            total_template += objects_to_str(pos_trace, counter_id, "pos")
        for neg_trace in neg_traces:
            counter_id += 1
            total_template += objects_to_str(neg_trace, counter_id, "neg")
        return total_template.strip()
    
    def solve_case(self, traces_dict):
        traces_gur = traces_dict
        # print(traces_gur)
        pos_ts, neg_ts = traces_dict['pos'], traces_dict['neg']
        traces_cli = self.traces_to_lp_local(pos_ts, neg_ts)
        # print(traces_cli)

        time_cli_start = perf_counter()
        print(self.clingo_exp.solve(traces_cli), end="\n")
        time_cli_end = perf_counter()

        time_gur_start = perf_counter()
        print(self.gurobi_exp.solve(traces_gur), end="\n")
        time_gur_end = perf_counter()

        print(f"tiempo clingo: {time_cli_end-time_cli_start} seconds")
        print(f"tiempo gurobi: {time_gur_end-time_gur_start} seconds")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Initial log")

    exp = Experiment(
        conn_path="./traces_ch/B6ByNegPMKs_connectivity.json",
        objs_path="./traces_ch/B6ByNegPMKs_objects.json",
        min_trace_steps=3,
        max_trace_steps=40,
        negative_traces_case=1,
        max_dag_nodes=10,
        max_dag_tries=5000,
        max_automata_states=10,
    )
    results = exp.run()
    print(results)
