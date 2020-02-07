from .wrapped_dict import WrappedDict


class WorldState(WrappedDict):
    """A model of the world state"""

    def __init__(self, *args, **kwargs):
        self.turn_number = 0
        super().__init__(*args, **kwargs)

    def automatic_tick(self):
        return

    def execution_tick(self):
        return

    def simulation_tick(self):
        self.automatic_tick()

    def real_tick(self):
        self.turn_number += 1
        self.automatic_tick()
        self.execution_tick()

    def describe(self):
        print(self.turn_number, self.wrapping())

    def child(self):
        c = super().child()
        c.turn_number = self.turn_number
        return c
