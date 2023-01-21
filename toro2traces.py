import os
import itertools
from clingo_vs_gurobi import Experiment

def from_toro_to_standar(trace_list: list) -> dict:
    trace_list
    trace_std = {'pos': [], 'neg': []}
    partial_trace = []
    for i in range(len(trace_list)):
        pred, sgn = trace_list[i]
        pred = [pred,] if pred else []
        partial_trace.append(pred)
        if sgn > 0.5:
            trace_std['pos'].append(partial_trace.copy())
        else:
            trace_std['neg'].append(partial_trace.copy())
    return trace_std


def remove_duplicates(list_of_lists):
    list_of_lists.sort()
    return [list_of_lists for list_of_lists, _ in itertools.groupby(list_of_lists)]


def merge_dicts(list_of_dicts: list) -> dict:
    final_dict = {'pos': [], 'neg': []}
    for dictionary in list_of_dicts:
        final_dict['pos'] += dictionary['pos']
        final_dict['neg'] += dictionary['neg']
    final_dict['pos'] = remove_duplicates(final_dict['pos'])
    final_dict['neg'] = remove_duplicates(final_dict['neg'])
    return final_dict


def toro_traces():
    BASE_PATH = "./toro_traces/"
    list_of_dicts = []
    for trace_file_path in os.listdir(BASE_PATH):
        with open(BASE_PATH + trace_file_path) as trace_file:
            full_trace = trace_file.read()
            trace_list = eval(full_trace)
            trace_dict = from_toro_to_standar(trace_list)
            list_of_dicts.append(trace_dict)
    return merge_dicts(list_of_dicts)

if __name__ == '__main__':
    exp = Experiment(
        conn_path="./traces_ch/B6ByNegPMKs_connectivity.json",
        objs_path="./traces_ch/B6ByNegPMKs_objects.json",
        min_trace_steps=3,
        max_trace_steps=40,
        negative_traces_case=1,
        max_dag_nodes=10,
        max_dag_tries=500,
        max_automata_states=5,
        )
    traces_dict = toro_traces()
    exp.solve_case(traces_dict)