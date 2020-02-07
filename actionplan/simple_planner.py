# very simple a* planner


from .world_state import WorldState

from collections import Counter

DEBUG = True


class Node:

    """A convenience class, given a state and a set of actions."""

    def __init__(self, state: WorldState, known_actions=[], action=None):
        self._state = state
        self.known_actions = known_actions
        self.action = action  # the action that brought us to this node

    def cost(self):
        if self.action:
            return self.action.cost()
        else:
            return 0

    def describe(self):
        if self.action:
            return self.action.name
        else:
            return "start"

    @property
    def state(self):
        """Return the frozen version of the state usable as a hash"""
        return self._state.as_tuple()

    def neighbors(self, tick=None):
        "yield the valid neighboring nodes in action space. apply the tick function if any"
        for action_class in self.known_actions:
            # instantiate action
            action = action_class(self._state)
            # get the new state (None if action is invalid)
            new_state = action()
            if new_state is None:
                continue
            else:
                new_state.simulation_tick()
                # create a new Node object with the new state
                yield Node(new_state, known_actions=self.known_actions, action=action)

    def meets_goal(self, goal_state):
        """Does this node meet this goal_state"""
        return all(self._state.get(key) == value for key, value in goal_state.items())

    def distance_from_goal(self, goal_state):
        """How "far" is this node from the goal state"""
        # currently, this is a very naive heuristic, merely measuring how many of
        # the goal state conditions are satisfied
        return sum(self._state.get(key) != value for key, value in goal_state.items())


class Action:
    """
    Initialized with a world state, when called, it checks if it can operate
    upon that state, and if so, returns the modified state. If it can't operate
    (the initial state is invalid), returns None.

    Also provides a .cost(), which returns a number expressing how
    expensive the action is.

    """

    pre_conditions = {}
    state_change = {}
    _cost = 1

    def __init__(self, world_state: WorldState):
        # wrap the passed-in world-state
        self.state = world_state

    def valid(self):
        return all(
            self.state.get(key) == value for key, value in self.pre_conditions.items()
        )

    def create_child_state(self):
        self.state = self.state.child()

    def update_state(self):
        self.state.update(self.state_change)

    def __call__(self):
        if self.valid():
            self.create_child_state()
            self.update_state()

            return self.state

    def cost(self):
        return self._cost


class PathFinder:
    def __init__(self, start, goal_state, state_tick=None):
        self._found_path = []
        self.start_node = start
        self.goal_state = goal_state
        self.state_tick = state_tick

    def cost_function(self, x, y):
        """returns the g cost and h cost of the step from x to y"""
        return y.cost(), y.cost()

    def find_path(self):
        """A* path finding stupidly implemented"""

        if self._found_path:
            return self._found_path

        start = self.start_node

        cost_fn = self.cost_function

        # g is the cost of the path to the node
        # h is the heuristically-estimated distance to the goal
        #    calculating this is _easy_ in physical pathfinding
        #    because you can use a euclidian distance, but in
        #    goal stuff, there's usually not a simple heuristic
        # f is the sum of g and h.

        # we'll use this to track the cheapest parent to each node
        parents = {start.state: None}

        # we'll store the calculated costs of each node
        cell_g_costs = {start.state: 0}  # distance along path
        cell_h_costs = {
            start.state: start.distance_from_goal(self.goal_state)
        }  # heuristic distance from dest
        cell_f_costs = {
            start.state: start.distance_from_goal(self.goal_state)
        }  # total cost

        # open cells are cells we have yet to comprehensively evaluate
        open_cells = {start.state: start}
        closed_cells = dict()

        goal_met = False
        counter = 0
        while open_cells:
            counter += 1
            if DEBUG:
                print(len(open_cells))
                #
                c = Counter(cell_f_costs[x] for x in open_cells.keys())
                print(c)
            # this is somewhat costly once the list of open cells gets large
            #
            current_position = min(open_cells.keys(), key=cell_f_costs.get)
            current = open_cells[current_position]
            # print("evaluating", current, current.state)
            current_g = cell_g_costs[current.state]
            closed_cells[current.state] = current
            # print("open", len(open_cells), "closed", len(closed_cells))
            del open_cells[current.state]
            if current.meets_goal(self.goal_state):
                goal_met = True
                break
            for n_cell in current.neighbors(tick=self.state_tick):
                if n_cell.state in closed_cells:
                    continue
                g, h = cost_fn(current, n_cell)
                cell_h_costs[n_cell.state] = h
                total_g = current_g + g
                # print(" ", g, h, end="")
                if total_g < cell_g_costs.get(n_cell, 99):
                    # print(" new", total_g, end="")
                    parents[n_cell.state] = current
                    cell_g_costs[n_cell.state] = total_g
                    cell_f_costs[n_cell.state] = total_g + h
                    open_cells[n_cell.state] = n_cell
                # print()
        if not goal_met:
            raise ValueError

        self._path_distance = cell_f_costs[current.state]
        self._remaining_distance = cell_h_costs[current.state]

        path = []
        next_cell = current

        # print(parents)
        print("## considered", counter, "cells")
        while next_cell:
            path.insert(0, next_cell)
            next_cell = parents[next_cell.state]
        self._found_path = path  # cache it
        return path
