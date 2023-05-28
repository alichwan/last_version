"""God class
"""

from prefixtree import PrefixTree


class God:
    """
    Function
    """

    def __init__(self, traces):
        self.predicates = God.create_preds_vector(traces)
        self.ev2binpr = God.event2binpreds(self.predicates)
        self.arbol = PrefixTree(traces, self.ev2binpr)

    @staticmethod
    def create_preds_vector(traces):
        """
        Function
        """
        predicates = set()
        for sgn in ["pos", "neg"]:
            for trace in traces[sgn]:
                for event in trace:
                    predicates = predicates.union(set(event))
        return sorted(tuple(predicates))

    @staticmethod
    def event2binpreds(predicates):
        """
        Function that returns a function thats takes a list of predicates and
        gives a binary tuple of predicates
        """

        def e2b(event):
            return tuple(int(obj in event) for obj in predicates)

        return e2b

    def give_me_the_plant(self):
        """
        Function
        """
        return self.arbol


if __name__ == "__main__":
    pass
