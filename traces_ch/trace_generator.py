import numpy as np
import pandas as pd
import json
import os
import logging



def read_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def objects_to_str(obj_trace: list, trace_id: int, sign: str):
    template = ""
    template += f"{sign}Trace({trace_id}).\n"
    for time in range(len(obj_trace)):
        for obj in obj_trace[time]:
            template += (
                f"trace({trace_id},{str(obj).replace(' ', '_')},{time}).\n"
            )
    return f"\n{template.strip()}\n"


def random_walk(start: str, connections: dict, steps: int):
    pos_trace = []
    alternatives = []
    actual = start
    previo = None
    pos_trace.append(actual)
    for step in range(steps):
        #implementación actual: tomar todos los nodos posibles aunque este devolviendose, 
        #pues así se minimiza el caso de no tener la trace con la cantidad pedida de steps
        options = connections[actual] #[op for op in connections[actual] if op != previo]
        previo = actual
        if not options:
            logging.warning(f"Trace truncada por falta de opciones: {step}/{steps}")
            break
        actual = np.random.choice(options)
        pos_trace.append(actual)
        alternatives.append([op for op in options if op != actual])
    for i in range(1, len(pos_trace)): 
        alternatives.append(pos_trace[:i])
    return pos_trace, alternatives


def alternative_traces(pos_trace, alternatives):
    alts_traces = [
        [*pos_trace[: t + 1], alt]
        for t in range(len(alternatives))
        for alt in alternatives[t]
    ]
    return alts_traces


def traces_to_objects(trace: list, objects: dict):
    return [objects[connection_id] for connection_id in trace]


def gen_traces_file(pos_trace: list, neg_traces: list, objects: dict):
    total_template = ""
    counter_id = 1
    pos_objects = traces_to_objects(pos_trace, objects)
    total_template += objects_to_str(pos_objects, counter_id, "pos")
    for neg_trace in neg_traces:
        counter_id += 1
        neg_objects = traces_to_objects(neg_trace, objects)
        total_template += objects_to_str(neg_objects, counter_id, "neg")
    return total_template.strip()


def check_trace(pos_trace: list, objects: dict):
    last_location = pos_trace[-1]
    last_elements = objects[last_location]
    return len(last_elements) > 0


def generate_trace(p: int, connections: dict, objects: dict):
    start = np.random.choice([*connections.keys()])
    while 1:
        pos_trace, alternatives = random_walk(start, connections, p)
        if check_trace(pos_trace, objects):
            break
    neg_traces = alternative_traces(pos_trace, alternatives)
    total_template = gen_traces_file(pos_trace, neg_traces, objects)
    return total_template


if __name__ == "__main__":
    currente = (os.curdir)
    connections = read_json("./B6ByNegPMKs_connectivity.json")
    objects = read_json("./B6ByNegPMKs_objects.json")

    p = 2
    total_template = generate_trace(p, connections, objects)
    print(total_template)

    # with open("traces.lp", "w") as file:
    #     file.write(total_template)

    # print(total_template)
