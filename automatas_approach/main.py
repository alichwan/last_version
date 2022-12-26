import numpy as np
import pandas as pd
import json


class Node(object):
    _id = 0

    def __init__(self, parent_id=None, sigma=None):
        self._id = Node._id
        Node._id += 1

        self.parent_id = parent_id
        self.sigma = sigma
        self.sign = None


class PrefixTree:

    def __init__(self, traces, e2b):
        self.ev2binpr = e2b
        self.root = Node()
        self.id_nodes = {0: self.root}
        self.tree = {0: dict()}
        self.Sigma = set()
        self.sat = True
        self.process_traces(traces)

    def process_traces(self, traces):
        for sgn in ["neg", "pos"]:
            for trace in traces[sgn]:
                self.new_trace(trace, sgn)

    def new_trace(self, trace, sign):
        actual_id = 0
        actual_dict = self.tree
        actual_node = self.id_nodes[actual_id]
        for event in trace:
            trace_key = self.ev2binpr(event)  # lo codificamos en sigma
            self.Sigma.add(trace_key)  # agregamos al alfabeto
            partial_id = actual_dict[actual_id].get(trace_key)

            if partial_id != None:
                actual_id = partial_id
                actual_dict = actual_dict[actual_id]
                actual_node = self.id_nodes[actual_id]
            else:
                new_node = Node(parent_id=actual_node._id, sigma=trace_key)
                new_id = new_node._id
                self.id_nodes[new_id] = new_node

                actual_node = self.id_nodes[new_id]

                actual_dict[actual_id][new_id] = dict()
                actual_dict = actual_dict[actual_id]

                actual_id = new_id

        if (actual_node.sign != sign) and (actual_node.sign is not None):
            print("INSATISFIABLE TREE FOR NODE SIGNS")
            print(actual_node.sign, sign)
            self.sat = False
        actual_node.sign = sign

    def print_tree(self):
        print(json.dumps(self.tree, indent=2))

    def parent(self, node_id):
        return self.id_nodes[node_id].parent_id
    
    def sigma(self, node_id):
        return self.id_nodes[node_id].sigma
    
    def node_sgn(self, node_id):
        return self.id_nodes[node_id].sign 
    
    def F_pos(self):
        return [id_n for id_n in self.id_nodes if self.node_sgn(id_n) == "pos"]

    def F_neg(self):
        return [id_n for id_n in self.id_nodes if self.node_sgn(id_n) == "neg"]

    def show_signs(self):
        return {k: v.sign for k,v in self.id_nodes.items()}


class God:
    def __init__(self, all_traces):
        predicates = create_preds_vector(all_traces)

        ev2binpr = event2binpreds(predicates)

        self.arbol = make_tree(all_traces, ev2binpr)
    
    def give_me_the_plant(self):
        return self.arbol

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


def gen_traces_list(pos_trace: list, neg_traces: list, objects: dict):
    traces_objects_for_tree = {"pos": [], "neg": []}
    pos_objects = traces_to_objects(pos_trace, objects)
    traces_objects_for_tree["pos"].append(pos_objects)
    for neg_trace in neg_traces:
        neg_objects = traces_to_objects(neg_trace, objects)
        traces_objects_for_tree["neg"].append(neg_objects)
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
    for sgn in ["pos", "neg"]:
        for trace in all_traces[sgn]:
            for event in trace:
                predicates = predicates.union(set(event))
    return tuple(predicates)


def event2binpreds(predicates):
    def e2b(ev):
        return tuple(int(obj in ev) for obj in predicates)

    return e2b


def make_tree(traces, e2b):
    tree = PrefixTree(traces, e2b)
    return tree


if __name__ == "__main__":
    connections = read_json("../traces_ch/B6ByNegPMKs_connectivity.json")
    objects = read_json("../traces_ch/B6ByNegPMKs_objects.json")
    p = 2

    all_traces = generate_trace(p, connections, objects)
    predicates = create_preds_vector(all_traces)

    ev2binpr = event2binpreds(predicates)

    print(predicates)
    arbol = make_tree(all_traces, ev2binpr)

    arbol.print_tree()
    print(arbol.sat)
    print(arbol.Sigma)
    print(arbol.id_nodes)
    # print(arbol.id_nodes[5].parent)

