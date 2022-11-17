import numpy as np
import pandas as pd
import json


class Node:
    def __init__(self, event2bin, value=None):
        '''
        Create a node (vertex) of the tree

        Parameters
        ----------
        value : int
            Represent the value stored in the node: positive or negative
        '''
        self.event2bin = event2bin
        self.value = value
        self.children = dict()
        self.sat = True

    def set_child(self, trace, sign):
        '''
        Add a child node as left or right child to the current node

        Parameters
        ----------
        trace : str
            Trace of the events which define the path
        sign : str
            Represent the sign of the trace, if a child is positive and negative the tree es insatisfacible
        '''
        # vemos si queda trace o se acabó
        if len(trace) > 0:
            event = trace.pop(0)
            trace_key = self.event2bin(event)
            # vemos si existe el camino
            branch = self.children.get(trace_key)
            if branch:
                # self.children[trace_key].set_child(trace, sign)
                branch.set_child(trace, sign)
            else:
                self.children[trace_key] = Node(self.event2bin)
                self.children[trace_key].set_child(trace, sign)
        else:
            if (self.value is not None) and (self.value != sign):
                print('INSATISFIABLE TREE FOR NODE SIGNS')
                print(self.value, sign)
                self.sat = False
            self.value = sign

    def __str__(self):
        return str(self.value)


class CompTree:
    '''
    Create a new tree
    Parameters
    ----------
    root : Node
    Represent the root of the tree
    '''

    def __init__(self, ev2binpr, root=None):
        self.root = root if root else Node(ev2binpr)

    def process_traces(self, traces):
        for sgn in ['neg', 'pos']:
            for trace in traces[sgn]:
                self.root.set_child(trace=trace, sign=sgn)

    def sat(self):
        sat = True
        watching = [self.root]
        while watching:
            actual = watching.pop(0)
            sat = sat and actual.sat
            watching += [n for n in actual.children.values()]
        return sat

    def print_tree(self, root=None, key=None, level=0):
        root = root if root else self.root
        if level > 0:
            print('\t' * level, f'{key}->', root)
        else: 
            print('() -> root')
        for key, child in root.children.items():
            self.print_tree(child, key, level + 1)


def read_json(path):
    with open(path, 'r') as json_file:
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


def event2binpreds(predicates):
    def e2b(ev):
        return tuple(int(obj in ev) for obj in predicates)
    return e2b


def make_tree(traces, e2bp):
    tree = CompTree(e2bp)
    tree.process_traces(traces)
    tree.print_tree()
    print(tree.sat())


if __name__ == '__main__':
    connections = read_json('../traces_ch/B6ByNegPMKs_connectivity.json')
    objects = read_json('../traces_ch/B6ByNegPMKs_objects.json')
    p = 5
    all_traces = generate_trace(p, connections, objects)
    predicates = create_preds_vector(all_traces)

    ev2binpr = event2binpreds(predicates)
    
    print(predicates)
    make_tree(all_traces, ev2binpr)
