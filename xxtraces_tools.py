"""
Module that contains some basic functionality used by most of the modules.
"""
import json
import numpy as np


def read_json(path: str):
    """
    Function thats read a json file
    """
    with open(path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def random_walk(start: str, connections: dict, steps: int) -> tuple:
    """
    Function that given a graph of connections, a starting point and
    a number of steps, generates a random path in that graph and all
    the alternatives nodes that could be visited.
    """
    pos_trace = []
    alternatives = []
    actual = start
    pos_trace.append(actual)
    for _ in range(steps):
        options = connections[actual]
        actual = np.random.choice(options)
        pos_trace.append(actual)
        alternatives.append([op for op in options if op != actual])
    for i in range(1, len(pos_trace)):
        alternatives.append(pos_trace[:i])
    return pos_trace, alternatives


def alternative_traces(pos_trace, alternatives):
    """
    Function thats expands the alternative trace that could be obtained
    """
    alts_traces = [
        [*pos_trace[: t + 1], alt]
        for t, alts in enumerate(alternatives)
        for alt in alts
    ]
    return alts_traces


def traces_to_objects(trace: list, objects: dict):
    """
    Function that get the objects of each room in the trace
    """
    return [objects[connection_id] for connection_id in trace]


def gen_traces_dict(pos_trace: list, neg_traces: list, objects: dict) -> dict:
    """
    Function that returns a dictionary with the positive and negatives traces
    """
    traces_object_dict = {"pos": [], "neg": []}
    pos_objects = traces_to_objects(pos_trace, objects)
    traces_object_dict["pos"].append(pos_objects)
    for neg_trace in neg_traces:
        neg_objects = traces_to_objects(neg_trace, objects)
        traces_object_dict["neg"].append(neg_objects)
    return traces_object_dict


def check_trace(pos_trace: list, objects: dict) -> bool:
    """
    Function that checks if a trace is valid. This is, the last room in
    th trace has objects.
    """
    last_location = pos_trace[-1]
    last_elements = objects[last_location]
    return bool(last_elements)


def gen_template_clingo(pos_trace: list, neg_traces: list, objects: dict):
    """
    Function
    """
    total_template = ""
    counter_id = 1
    pos_objects = traces_to_objects(pos_trace, objects)
    total_template += objects_to_str(pos_objects, counter_id, "pos")
    for neg_trace in neg_traces:
        counter_id += 1
        neg_objects = traces_to_objects(neg_trace, objects)
        total_template += objects_to_str(neg_objects, counter_id, "neg")
    return total_template.strip()


def get_valid_walk(trace_steps: int, connections: dict, objects: dict):
    """
    Function that returns a positive trace and some alternative ones
    """
    start = np.random.choice([*connections.keys()])
    while 1:
        pos_trace, alternatives = random_walk(start, connections, trace_steps)
        if check_trace(pos_trace, objects):
            return pos_trace, alternatives


def pos_negs_traces(trace_steps: int, connections: dict, objects: dict):
    """
    Function that given a connection graph builds a positivetrace and a list
    of negative traces
    """
    pos_trace, alternatives = get_valid_walk(trace_steps, connections, objects)
    neg_traces = alternative_traces(pos_trace, alternatives)
    return pos_trace, neg_traces


def generate_trace_clingo(trace_steps: int, connections: dict, objects: dict):
    """
    Function that generates a template of traces given connections and a number
    of steps
    """
    pos_trace, neg_traces = pos_negs_traces(trace_steps, connections, objects)
    return gen_template_clingo(pos_trace, neg_traces, objects)


def generate_trace_gurobi(trace_steps: int, connections: dict, objects: dict):
    """
    Function that generates a dictionary of traces given connections and a number
    of steps
    """
    pos_trace, neg_traces = pos_negs_traces(trace_steps, connections, objects)
    return gen_traces_dict(pos_trace, neg_traces, objects)


def objects_to_str(obj_trace: list, trace_id: int, sign: str):
    """
    Function
    """
    template = ""
    template += f"{sign}Trace({trace_id}).\n"
    for time, objects in enumerate(obj_trace):
        for obj in objects:
            template += (
                f"trace({trace_id},{str(obj).replace(' ', '_')},{time}).\n"
            )
    return f"\n{template.strip()}\n"


def read_traces_file(traces_file_path: str):
    """
    Function that reads the lines from a a trace file
    """
    with open(traces_file_path, "r", encoding="utf-8") as traces:
        lines = traces.readlines()
        lines = [line.strip("trace(). \n") for line in lines if line.strip()]
        return lines


if __name__ == "__main__":
    pass
