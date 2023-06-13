"""Module that contains the class for create random traces 
from a given graph
"""
import numpy as np
from traces_ch.trace_generator import (
    read_json,
    check_trace,
    alternative_traces,
    traces_to_objects,
    gen_traces_file,
    objects_to_str,
)


class Graph:
    """Graph class to get traces"""

    def __init__(
        self,
        connections_path: str,
        objects_path: str,
        negative_traces_case: int = 2,
    ):
        self.connections = read_json(connections_path)
        self.objects = read_json(objects_path)
        self.negative_traces_case = negative_traces_case

    def random_walk(self, start: str, steps: int):
        """get random walk in the graph

        Args:
            start (str): id of the initial node in the graph
            steps (int): number of steps that the walk should have

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        pos_trace = []
        alternatives = []
        actual = start
        pos_trace.append(actual)
        for _ in range(steps):
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
        """Create a random trace from a given graph, with n_steps steps

        Args:
            n_steps (int): Number of steps that have the positive trace

        Returns:
            Dict[str: List[List[str]]]

        pos_trace: list of positive traces
        neg_trace: list of negative traces
        """
        tries_per_start = 100
        while 1:
            actual_try = 1
            start = np.random.choice([*self.connections.keys()])
            while actual_try <= tries_per_start:
                pos_trace, alternatives = self.random_walk(start, n_steps)
                if check_trace(pos_trace, self.objects):
                    neg_traces = alternative_traces(pos_trace, alternatives)
                    return self.dict_to_objects(
                        {
                            "pos": [
                                pos_trace,
                            ],
                            "neg": neg_traces,
                        }
                    )
                actual_try += 1

    def same_last_node_traces(self, n_steps: int):
        """Method to create a dict of traces positives and negatives where
        the positive one is given by a random walk through a graph with n steps.
        The negative ones will be all the alternative ways to reach the same last node
        as the positive one, but using at most n+2 steps.

        Args:
            n_steps (int): Number of steps that the random walk should have
        """
        assert n_steps >= 3
        n_steps_traces = list()
        candidate_neg_traces = list()

        last_node = np.random.choice([*self.connections.keys()])
        old_list = [
            [
                last_node,
            ],
        ]
        new_list = list()
        while old_list:
            for current_trace in old_list:
                if len(current_trace) >= 2:
                    last_node = current_trace[-2]
                current_node = current_trace[-1]
                neighbors = self.connections[current_node]
                for neighbor in neighbors:
                    # if neighbor == last_node:
                    #     continue
                    new_trace = current_trace + [
                        neighbor,
                    ]
                    new_list.append(new_trace)
                    if len(new_trace) == n_steps and check_trace(
                        new_trace, self.objects
                    ):
                        n_steps_traces.append(new_trace)
                        continue
                    if len(new_trace) >= n_steps + 3:
                        pos_idx = np.random.choice(range(len(n_steps_traces)))
                        positive = n_steps_traces.pop(pos_idx)
                        almost_negatives = n_steps_traces
                        almost_negatives += candidate_neg_traces
                        negatives = [
                            trace
                            for trace in almost_negatives
                            if positive[-1] in trace
                        ]
                        return self.dict_to_objects(
                            {
                                "pos": [
                                    positive,
                                ],
                                "neg": negatives,
                            }
                        )
                    candidate_neg_traces.append(new_trace)
                old_list = new_list
                new_list = list()
        print("Error, last node not considered", last_node, old_list)

    def dict_to_objects(self, id_traces: dict):
        """We must convert those traces with ids to traces with objects

        Args:
            id_traces (dict): traces with a list of room ids
        """
        obj_traces = {"pos": [], "neg": []}
        for sgn in ["pos", "neg"]:
            for trace in id_traces[sgn]:
                obj_traces[sgn].append([self.objects[step] for step in trace])
        return obj_traces


if __name__ == "__main__":
    pass
