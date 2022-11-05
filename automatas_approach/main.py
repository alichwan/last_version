# TODO:
# - tomar el grafo y hacer un vector que represente todos los predicados (detectores) disponibles
# - dada un conjunto de traces positivas P y negativas N, EN FORMATO LISTA DE CONJUNTOS DE PREDICADOS, construir un arbol
#   - se parte por un nodo raíz
#   - por cada trace, se toma cada una de las combinaciones de predicados, si existe esa combinación, se sitúa en el siguiente nodo
#   - si no existe la combinacion, se agrega un nuevo camino, se situa en el siguiente nodo
#   - al llegar a cada hoja su valor toma si es positivo o negativo
#

import numpy as np
import pandas as pd
import json

# https://www.bogotobogo.com/python/python_graph_data_structures.php
class Vertex:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

# puede ser

def read_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def random_walk(start: str, connections: dict, steps: int):
    pos_trace = []
    alternatives = []
    actual = start
    pos_trace.append(actual)
    for step in range(steps):
        options = connections[actual]
        actual = np.random.choice(options)
        pos_trace.append(actual)
        # alternatives.append([op for op in options if op != actual])
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


def gen_traces_list(pos_trace: list, neg_traces: list, objects: dict):
    traces_objects_for_tree = {'pos': [], 'neg': []}
    pos_objects = traces_to_objects(pos_trace, objects)
    traces_objects_for_tree['pos'].append(pos_objects)
    for neg_trace in neg_traces:
        neg_objects = traces_to_objects(neg_trace, objects)
        traces_objects_for_tree['neg'].append(neg_objects)
    return traces_objects_for_tree


def check_trace(pos_trace: list, objects: dict):
    last_location = pos_trace[-1]
    last_elements = objects[last_location]
    return bool(last_elements)


def generate_trace(p: int, connections: dict, objects: dict):
    start = np.random.choice([*connections.keys()])
    while 1:
        pos_trace, alternatives = random_walk(start, connections, p)
        if check_trace(pos_trace, objects):
            break
    neg_traces = alternative_traces(pos_trace, alternatives)
    all_traces = gen_traces_list(pos_trace, neg_traces, objects)
    return all_traces


def create_preds_vector(all_traces):
    predicates = set()
    for sgn in ['pos', 'neg']:
        for trace in all_traces[sgn]:
            for event in trace:
                predicates = predicates.union(set(event))
    return tuple(predicates) 


def event2binpreds(event, predicates):
    return tuple(int(obj in event) for obj in predicates)


def make_tree(traces, e2bp):
    tree = {root: None}


def create_traces():
    pass



if __name__ == "__main__":
    connections = read_json("../traces_ch/B6ByNegPMKs_connectivity.json")
    objects = read_json("../traces_ch/B6ByNegPMKs_objects.json")
    p = 7
    all_traces = generate_trace(p, connections, objects)
    predicates = create_preds_vector(all_traces)

    ev2binpr = event2binpreds(all_traces['pos'][0][-1], predicates)

