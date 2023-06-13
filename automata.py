"""Automata class
"""
from graph_drawing import from_automata_to_graph


class AutomataBase:
    """
    Automata base class
    """

    def __init__(self):
        self._delta = {}
        self._final_states = []
        self.state_signs = {}

    def delta(self, state, sigma):
        """
        Function that returns the state resulting from read the word sigma in
        state.

        Here we assume that if the transition is not defined, then we stay
        in the same state.
        """
        next_state = self._delta.get((state, sigma), state)
        return next_state

    def process_just_one_trace(self, trace: list):
        """
        Function to process just one trace and return if the signs are equal
        """
        state = 0
        for step in trace:
            sigma = self.room2sigma(step)
            state = self.delta(state, sigma)
        return state

    def check_traces(self, traces_dict: dict):
        """Function that checks if traces are processed as they should

        Args:
            traces_dict (dict[str: list]): {"pos": traces, "neg": traces}

        returns:
            bool: True if traces are the sign that they should
        """
        for sgn, traces in traces_dict.items():
            for trace in traces:
                state = self.process_just_one_trace(trace)
                if self.state_signs[state] != sgn:
                    return False
        return True

    def set_signs(self, positive_nodes: list, negative_nodes: list) -> None:
        """Setting signs of each automaton state. Receives the nodes of the
        PrefixTree, and considering the mapping node-to-state, set the sign
        of the states

        Args:
            positive_nodes (list): list of nodes that are positive
            negative_nodes (list): list of nodes that are negative
        """

    def room2sigma(self, room: list):
        """Given a certain set, tuple or list of elements in a room, get
        the automaton representation (sigma) of that elements.

        Args:
            room (List[str]): list with elements in the room
        """
        print("Not implemented yet", room)
        return room

    def plot(self):
        """Function that plots a graph representation of the automata,
        considering the nodes and deltas
        """
        from_automata_to_graph(self._delta, self._final_states)

    def __repr__(self):
        """Override representation to print"""
        representation = ""
        sigmas = list({sigma for (st1, sigma) in self._delta})
        states = list({st1 for (st1, sigma) in self._delta})
        deltas = [
            (st1, sigma, self.delta(st1, sigma))
            for st1 in states
            for sigma in sigmas
            if self.delta(st1, sigma) != st1
        ]
        deltas = sorted(deltas)
        for st1, sigma, st2 in deltas:
            state1 = f"({st1}:{self.state_signs[st1]})"
            state2 = f"({st2}:{self.state_signs[st2]})"
            representation += f"{state1}--[{sigma}]-->{state2}\n"
        return representation

    def __len__(self):
        """Returns the length of the _delta dictionary"""
        return len(self.state_signs)

    def __eq__(self, other):
        """Fucntion that checks if the representation of the automatas are
        equivalent

        Args:
            other (AutomataBase): An instance of a subclass of AutomataBase

        Raises:
            ValueError: _description_
            ValueError: _description_
            AttributeError: _description_

        Returns:
            bool: _description_
        """
        if len(self) != len(other):
            return False

        print("state_signs")
        print(self.state_signs)
        print(other.state_signs)

        my_auto = set(repr(self).strip().split())
        other_auto = set(repr(other).strip().split())
        print("\nyo\\otro", my_auto.difference(other_auto))
        print("\notro\\yo", other_auto.difference(my_auto))
        symdiff = my_auto ^ other_auto
        print("symdiff=", symdiff)
        print("\n\nInter:", my_auto.intersection(other_auto))
        return not symdiff


class Automata(AutomataBase):
    """
    Automata class that encapsulates the information of
    the milp solution
    """

    def __init__(self, solution, e2b):
        super().__init__()
        self._node_to_state = {
            nq[0]: nq[1]
            for nq, val in solution["n_to_q"].items()
            if val.x > 0.5
        }
        self._is_used = {q for n, q in self._node_to_state.items()}
        self._delta = {
            (k[0], k[1]): k[2]
            for k, v in solution["delta"].items()
            if v.x > 0.5 and k[0] in self._is_used and k[2] in self._is_used
        }
        self._rev_sigma_dict = solution["rev_sigma_dict"]
        self._sigma_dict = solution["sigma_dict"]
        self._ssigma = list(self._sigma_dict.keys())
        self._event2binpreds = e2b
        self.state_signs = {state: None for state in self._is_used}

    def set_signs(self, positive_nodes: list, negative_nodes: list) -> None:
        """
        Args:
            positive_nodes ([int]): list of positive and acceptance nodes
            negative_nodes ([int]): list of negative nodes
        """
        for node in positive_nodes:
            state = self._node_to_state[node]
            self.state_signs[state] = "pos"
        for node in negative_nodes:
            state = self._node_to_state[node]
            if self.state_signs[state] == "pos":
                raise ValueError("Sign conflict")
            self.state_signs[state] = "neg"

    def room2sigma(self, room: list):
        """
        Function thats translate the detectors in a trace room into a sigma
        id from the milp execution
        """
        room_tuple = self._event2binpreds(room)
        return self._sigma_dict[room_tuple]

    def __repr__(self):
        """Override representation to print"""

        base_repr = super().__repr__()

        for idx, vals in self._rev_sigma_dict.items():
            sigma_str = f"{vals}".strip("()").replace(", ", "")
            base_repr = base_repr.replace(f"[{idx}]", f"[{sigma_str}]")
        return base_repr


class AutomataClingo(AutomataBase):
    """
    Automata class that encapsulates the information of
    the clingo solver solution
    """

    def __init__(self, solution, e2b):
        super().__init__()
        self._delta = {
            (int(value[0]), value[1].strip('"')): int(value[2])
            for value in solution["delta"]
        }
        self._node_to_state = {
            int(value[0]): int(value[1]) for value in solution["n_to_q"]
        }
        self._ssigma = solution["ssigma"]
        self._states_used = max(self._node_to_state.values())
        self._solver_signs = solution["states_signs"]  # See w to do with this
        self.state_signs = {
            state: None for state in range(self._states_used + 1)
        }
        self._final_states = []
        self._event2binpreds = e2b

    def set_signs(self, positive_nodes: list, negative_nodes: list) -> None:
        """
        Args:
            positive_nodes ([int]): list of positive and acceptance nodes
            negative_nodes ([int]): list of negative nodes
        """
        for node in positive_nodes:
            state = self._node_to_state[node]
            self.state_signs[state] = "pos"
            self._final_states.append(state)
        for node in negative_nodes:
            state = self._node_to_state[node]
            if self.state_signs[state] == "pos":
                raise ValueError("Sign conflict")
            self.state_signs[state] = "neg"

    def room2sigma(self, room: list):
        """
        Function thats translate the detectors in a trace room into a sigma
        id from the milp execution
        """
        try:
            room_tuple = self._event2binpreds(room)
            return f"{room_tuple}".strip("()").replace(", ", "")
        except TypeError as exc:
            raise AttributeError(
                "Attr '_event2binpreds' hasn´t been assigned"
            ) from exc


if __name__ == "__main__":
    pass
