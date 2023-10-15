import os
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from clingo_vs_gurobi import Experiment


def from_toro_to_standar(trace_list: list) -> dict:
    """
    Transforms a list of tuples into a list of lists keeping sign
    """
    trace_std = {"pos": [], "neg": []}
    partial_trace = []
    for i, _ in enumerate(trace_list):
        pred, sgn = trace_list[i]
        pred = (
            [
                pred,
            ]
            if pred
            else []
        )
        partial_trace.append(pred)
        if sgn > 0.5:
            trace_std["pos"].append(partial_trace.copy())
        else:
            trace_std["neg"].append(partial_trace.copy())
    return trace_std


def remove_duplicates(list_of_lists):
    """
    Removes duplicates from a list of lists
    """
    list_of_lists.sort()
    return [
        list_of_lists for list_of_lists, _ in itertools.groupby(list_of_lists)
    ]


def merge_dicts(list_of_dicts: list) -> dict:
    """
    Unifies the lists of each dictionary
    """
    final_dict = {"pos": [], "neg": []}
    for dictionary in list_of_dicts:
        final_dict["pos"] += dictionary["pos"]
        final_dict["neg"] += dictionary["neg"]
    final_dict["pos"] = remove_duplicates(final_dict["pos"])
    final_dict["neg"] = remove_duplicates(final_dict["neg"])
    return final_dict


def toro_traces():
    """
    Creates a dictionary of positive and negative traces from a list of files
    """
    base_path = "./toro_traces/"
    list_of_dicts = []
    for trace_file_path in os.listdir(base_path):
        with open(base_path + trace_file_path, encoding="utf-8") as trace_file:
            full_trace = trace_file.read()
            trace_list = eval(full_trace)
            trace_dict = from_toro_to_standar(trace_list)
            list_of_dicts.append(trace_dict)
    return merge_dicts(list_of_dicts)


def plot_connections(modelo, x, delta, c, f, Sigma_dict, arbol):
    EPS = 0.2
    G = nx.DiGraph()
    color_map = ["white" for q in f]
    for q in f:
        is_positive = any(
            [
                arbol.id_nodes[n].sign == "pos"
                for n in arbol.id_nodes
                if x[n, q].X > EPS
            ]
        )
        is_negative = any(
            [
                arbol.id_nodes[n].sign == "neg"
                for n in arbol.id_nodes
                if x[n, q].X > EPS
            ]
        )
        if is_positive:
            color_map[q] = "lime"
        if is_negative:
            color_map[q] = "tomato"
        if is_positive and is_negative:
            color_map[q] = "blue"
    for q, s, qp in delta:
        if q != qp and delta[q, s, qp].X > EPS:
            G.add_edge(q, qp)

    options = {
        "font_size": 18,
        "node_size": 700,
        "node_color": color_map,
        "edgecolors": "black",
        "linewidths": 2,
        "width": 2,
    }
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, **options)
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels={
            (q, qp): arbol.Sigma_simbol[Sigma_dict[s]]
            for q, s, qp in delta
            if q != qp and delta[q, s, qp].X > EPS and f[qp].X > EPS
        },
    )
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
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
    modelo, x, delta, c, f, Sigma_dict, arbol = exp.solve_case(traces_dict)
    plot_connections(modelo, x, delta, c, f, Sigma_dict, arbol)
