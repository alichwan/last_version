import networkx as nx
import matplotlib.pyplot as plt
import json


def read_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


connections = read_json("traces_ch/B6ByNegPMKs_connectivity.json")

name2num = dict([(k, i) for i, k in enumerate(connections.keys())])

G = nx.Graph()
for k, v in connections.items():
    for item in v:
        G.add_edge(name2num[k], name2num[item])


# explicitly set positions
options = {
    "font_size": 15,
    "node_size": 20,
    "node_color": "white",
    "edgecolors": "black",
    "arrowsize": 1000,
}
nx.draw_networkx(G, with_labels=False, **options)

# Set margins for the axes so that nodes aren't clipped
ax = plt.gca()
ax.margins(0.20)
plt.axis("off")
plt.show()
