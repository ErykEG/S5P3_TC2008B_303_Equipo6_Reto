# robot.py
from mesa.agent import Agent
import json

class Robot(Agent):

    def __init__(self, unique_id, model, x, y):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.nextPosition = None  # Initialize nextPosition

    def move(self):
        if self.nextPosition:
            self.model.grid.move_agent(self, self.nextPosition)
            self.pos = self.nextPosition
            self.nextPosition = None  # Reset nextPosition after moving

    def move_to_random_neighbor(self):
        x, y = self.pos
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.model.random.choice(neighbors)
        self.nextPosition = new_position
