from main import God, read_json
from MILP import milp
import networkx as nx
import matplotlib.pyplot as plt

EPS = 0.2
MAX_STATES = 7
traces_path = {
    "A": "./test_traces/A_oPoN.json",
    "B": "./test_traces/B_oPmN.json",
    "C": "./test_traces/C_mPoN.json",
    "D": "./test_traces/D_mPmN.json",
    "Z": "./test_traces/Z.json",
}

all_traces = read_json(traces_path["D"])

g = God(all_traces)
arbol = g.give_me_the_plant()


if arbol.sat:
    modelo, x, delta, c, f, Sigma_dict = milp(arbol, max_states=MAX_STATES)
    if modelo.Status == 2:
        G = nx.DiGraph()
        color_map = ["white" for q in f]
        
        # ver resultados
        for i in x:
            print(i, x[i].X) if x[i].X > eps else None
        
        for i in f:
            print(i, f[i].X) if f[i].X > eps else None
        
        for q, s, qp in delta:
            print(q,s,":",Sigma_dict[s],qp, delta[q, s, qp].X) if q != qp and delta[q, s, qp].X > eps else None

        # print(c)
        # print(x)
        # print(f)
        # print(delta)

        print(arbol.show_signs())

        for q in f:
            # print([arbol.id_nodes[n].sign == "neg" for n in arbol.id_nodes if x[n,q].X > eps] )
            # print([arbol.id_nodes[n].sign for n in arbol.id_nodes if x[n,q].X > eps] )

            is_positive = any([arbol.id_nodes[n].sign == "pos" for n in arbol.id_nodes if x[n,q].X > eps] )
            is_negative = any([arbol.id_nodes[n].sign == "neg" for n in arbol.id_nodes if x[n,q].X > eps] )
            if is_positive: 
                color_map[q] = "lime" 
            if is_negative: 
                color_map[q] = "tomato"
            if is_positive and is_negative: 
                color_map[q] = "blue" 
        for q, s, qp in delta:
            if q != qp and delta[q, s, qp].X > eps:
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
            G, pos,
            edge_labels={(q, qp): Sigma_dict[s] for q, s, qp in delta if q != qp and delta[q, s, qp].X > eps and f[qp].X > eps}
        )
        plt.axis('off')
        plt.show()


    elif modelo.Status == 3:
        print("Modelo insatisfacible, ID de status:", modelo.Status)
    else:
        print("Ststus id: ", modelo.Status)





