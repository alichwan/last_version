"""module that contains the prefix (or compute) tree class
"""
import itertools


class Node(object):
    """
    Node class to codify prefix tree
    """

    new_id = itertools.count()

    def __init__(self, parent_id=None, sigma=None):
        """
        Function
        """
        self.node_id = next(Node.new_id)

        self.parent_id = parent_id
        self.sigma = sigma
        self.sign = None
        self.children = {}

    @staticmethod
    def reset_id() -> None:
        """Function that makes the index of nodes start from 0 again
        instead keep counting
        """
        Node.new_id = itertools.count()


class PrefixTree:
    """
    Prefix Tree that codes the traces. The nodes could be positive, negatives
    or None depending on the sign of the trace.
    """

    def __init__(self, traces, e2b):
        self.ev2binpr = e2b
        self.root = Node()
        self.id_nodes = {0: self.root}
        self.Sigma_simbol = dict()
        self.Sigma = set()
        self.sat = True
        self.process_traces(traces)

    def process_traces(self, traces: dict) -> None:
        """
        Function
        """
        for sgn in ["neg", "pos"]:
            for trace in traces[sgn]:
                self.new_trace(trace, sgn)
        Node.reset_id()

    def new_trace(self, trace, sign):
        """
        Function
        """
        actual_id = 0
        actual_node = self.id_nodes[actual_id]
        actual_dict = actual_node.children
        for event in trace:
            trace_key = self.ev2binpr(event)  # lo codificamos en sigma
            self.Sigma.add(trace_key)  # agregamos al alfabeto
            self.Sigma_simbol[trace_key] = event
            partial_id = actual_dict.get(trace_key)  # conseguimos nodo

            if partial_id is None:
                new_node = Node(parent_id=actual_node.node_id, sigma=trace_key)
                new_id = new_node.node_id
                self.id_nodes[new_id] = new_node
                actual_dict[trace_key] = new_id

                actual_node = new_node
                actual_dict = actual_node.children
                actual_id = new_id
            else:
                actual_node = self.id_nodes[partial_id]
                actual_dict = actual_node.children
                actual_id = partial_id

        if (actual_node.sign != sign) and (actual_node.sign is not None):
            print("INSATISFIABLE TREE FOR NODE SIGNS")
            print(actual_node.sign, sign)
            node_id = actual_node.node_id
            print(f"Signos no cuadran, camino:{self.find_treepath(node_id)}")
            self.sat = False
        actual_node.sign = sign

    def find_treepath(self, node_id):
        """
        Function
        """
        rev_treepath = []
        rev_treepath.append(node_id)
        node = self.id_nodes[node_id]
        parent_id = node.parent_id
        while parent_id:
            rev_treepath.append(parent_id)
            node = self.id_nodes[parent_id]
            parent_id = node.parent_id
        return list(reversed(rev_treepath))

    def print_tree(self):
        """
        Function
        """
        print(self)

    def to_asp(self) -> str:
        """Function that writes in a file the tree as an automata in lp

        Args:
            path (str): Path and filename of the file to be written.
            Must have .lp extension
        """
        encoded_tree = ""
        # codificar nodos # node(n).
        for node_id in self.id_nodes:
            encoded_tree += "\n" if node_id != 0 else ""
            encoded_tree += f"node({node_id})."
            if node_id in self.f_state_pos():
                # codificar positivos # pos(n).
                encoded_tree += "\n"
                encoded_tree += f"pos({node_id})."
            if node_id in self.f_state_neg():
                # codificar negativos # neg(n).
                encoded_tree += "\n"
                encoded_tree += f"neg({node_id})."
        # codificar ramas # branch(n1, "0010", n2).
        sigmas_lp = set()
        for node in self.id_nodes.values():
            prev = node.parent_id
            if prev is None:
                continue
            sigma_lp = "".join(str(node.sigma).strip("()").split(", "))
            sigmas_lp.add(sigma_lp)
            encoded_tree += "\n"
            encoded_tree += f'branch({prev},"{sigma_lp}",{node.node_id}).'
        # codificar Sigma # sigma("0010").
        for sigma_lp in sigmas_lp:
            encoded_tree += "\n"
            encoded_tree += f'sigma("{sigma_lp}").'
        encoded_tree += "\n"
        return encoded_tree

    def parent(self, node_id):
        """
        Function
        """
        try:
            return self.id_nodes[node_id].parent_id
        except KeyError as error:
            print(error.__traceback__)

    def sigma(self, node_id):
        """
        Function
        """
        return self.id_nodes[node_id].sigma

    def node_sgn(self, node_id):
        """
        Function
        """
        return self.id_nodes[node_id].sign

    def f_state_pos(self):
        """
        Function
        """
        return [id_n for id_n in self.id_nodes if self.node_sgn(id_n) == "pos"]

    def f_state_neg(self):
        """
        Function
        """
        return [id_n for id_n in self.id_nodes if self.node_sgn(id_n) == "neg"]

    def show_signs(self):
        """
        Function
        """
        return {k: v.sign for k, v in self.id_nodes.items()}


if __name__ == "__main__":
    pass
