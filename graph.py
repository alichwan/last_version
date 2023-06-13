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
                    return {"pos": pos_trace, "neg": neg_traces}
                actual_try += 1


if __name__ == "__main__":
    pass
