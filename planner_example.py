from actionplan.simple_planner import Action, Node, PathFinder
from actionplan.world_state import WorldState
import random


class PieWorld(WorldState):
    def automatic_tick(self):
        # whipped cream degrades
        self.dec_to_zero("whipped_cream")

        if self.get("apple_sapling", 0) >= 5:
            # saplings become trees
            self["apple_tree"] = True
            self["apple_sapling"] = 0
        elif self.get("apple_sapling", 0) > 0:
            # saplings grow
            self.inc("apple_sapling")

    def x_execution_tick(self):
        if self["living_cow"] and random.randint(1, 20) >= 17:
            print("\tthe cow died.")
            self["living_cow"] = False
        if self["apple_tree"] and random.randint(1, 20) >= 16:
            print("\tthe apple tree died.")
            self["apple_tree"] = False


class BuyCow(Action):
    name = "buy cow"

    def valid(self):
        return (not self.state["living_cow"]) and self.state.get("gold", 0) > 12

    def update_state(self):
        self.state.dec("gold", 12)
        self.state["living_cow"] = True


class PlantTree(Action):
    name = "plant a tree"

    def valid(self):
        return not self.state["apple_tree"]

    def update_state(self):
        self.state["apple_sapling"] = 1


class SellApple(Action):
    name = "sell apples"

    def valid(self):
        return self.state.get("apples", 0) > 0

    def update_state(self):
        self.state.dec("apples")
        self.state.inc("gold", 1)


class SellMilk(Action):
    name = "sell milk"

    def valid(self):
        return self.state.get("fresh_milk", 0) > 0

    def update_state(self):
        milk = self.state["fresh_milk"]
        self.state["fresh_milk"] = 0
        self.state.inc("gold", 2 * milk)


class BuyPie(Action):
    name = "buy a pie"

    def valid(self):
        return self.state.get("gold", 0) > 8

    def update_state(self):
        self.state.dec("gold", 8)
        self.state["apple_pie"] = True


class MakeCrust(Action):
    name = "make_pie_crust"
    pre_conditions = {"pie_crust": False}
    state_change = {"pie_crust": True}


class MilkCow(Action):
    name = "milk_cow"

    def valid(self):
        return self.state["living_cow"] and self.state.get("raw_milk", 0) <= 3

    def update_state(self):
        self.state["raw_milk"] = self.state.get("raw_milk", 0) + 1
        self.state["milked_cow"] = True


class ProcessMilk(Action):
    name = "separate_cream"

    def valid(self):
        return self.state.get("raw_milk", 0) >= 1

    def update_state(self):
        milk = self.state["raw_milk"]
        self.state["raw_milk"] = 0
        self.state.inc("fresh_milk", milk)
        self.state.inc("fresh_cream", milk)


class WhipCream(Action):
    name = "whip_cream"

    def valid(self):
        return self.state.get("fresh_cream", 0) >= 1

    def update_state(self):
        self.state.dec("fresh_cream")
        self.state.inc("whipped_cream")
        self.state.inc("whipped_cream")


class PickApple(Action):
    name = "pick_apple"

    pre_conditions = {"apple_tree": True}

    def valid(self):
        return self.state["apple_tree"] and self.state.get("apples", 0) <= 8

    def update_state(self):
        wd = self.state
        wd["apples"] = wd.get("apples", 0) + 1


class BakePie(Action):
    name = "bake_pie"

    def valid(self):
        return (self.state.get("apples", 0) >= 4) and (
            self.state.get("pie_crust") is True
        )

    def update_state(self):
        wd = self.state
        wd["apples"] = wd["apples"] - 4
        wd["pie_crust"] = False
        wd["apple_pie"] = True
        wd["baked_pie"] = True


class EatPie(Action):
    name = "eat_pie"

    pre_conditions = {"apple_pie": True, "whipped_cream": 1}
    state_change = {"apple_pie": False, "hungry": False}


class Labor(Action):
    name = "do odd jobs"

    def update_state(self):
        self.state.inc("gold", 0.5)


initial_state = PieWorld(
    {
        "apple_tree": True,
        "hungry": True,
        "apple_pie": False,
        "pie_crust": False,
        "living_cow": True,
        "gold": 0,
        "whipped_cream": 0,
    }
)

all_actions = (
    PickApple,
    BakePie,
    EatPie,
    MakeCrust,
    MilkCow,
    ProcessMilk,
    WhipCream,
    SellMilk,
    BuyPie,
    PlantTree,
    SellApple,
    BuyCow,
    Labor,
)


def main():
    current_node = Node(initial_state, all_actions)
    while current_node:
        current_state = current_node._state
        pf = PathFinder(current_node, {"hungry": False})

        current_plan = pf.find_path()

        # start_node, next_node, _
        if len(current_plan) < 2:
            break
        print("# current plan:", ";".join(node.describe() for node in current_plan[1:]))
        break
        next_node = current_plan[1]
        action_class = type(next_node.action)

        action = action_class(current_state)

        next_state = action()
        print(">", action.name)
        # print(next_state)
        next_state.real_tick()
        next_state.describe()

        current_node = Node(next_state, next_node.known_actions, action=action)


if __name__ == "__main__":
    main()
