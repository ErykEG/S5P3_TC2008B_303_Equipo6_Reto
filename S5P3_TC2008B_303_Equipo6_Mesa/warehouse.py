from mesa.model import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from typing import List, Dict
from robot import Robot
import json
import numpy as np

class Warehouse(Model):

    def __init__(self, width: int, height: int, num_agents: int):
        # Initialize grid
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)

        # Available positions
        dispPos = [pos for _, pos in self.grid.coord_iter()]

        # Assign ids and place robots on the grid
        for id in range(num_agents):
            initial_pos = self.random.choice(dispPos)
            robot = Robot(id, self, *initial_pos)
            self.grid.place_agent(robot, initial_pos)
            self.schedule.add(robot)

        # Data collector
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid},
        )

    def get_positions(self) -> List[Dict[str, int]]:
        positions = []
        for agent in self.schedule.agents:
            if isinstance(agent, Robot):
                positions.append({"x": agent.pos[0], "y": agent.pos[1]})
        return positions

    def positions_to_json(self) -> str:
        positions = self.get_positions()
        return json.dumps({"data": positions})

    def step(self):
        # Move robots
        for robot in self.schedule.agents:
            if isinstance(robot, Robot):
                robot.move_to_random_neighbor()
                robot.move()

        # Collect data
        self.datacollector.collect(self)

        # Perform model step
        self.schedule.step()

# Get positions of robots
def get_grid(model: Model) -> np.ndarray:
    grid = np.zeros((model.grid.width, model.grid.height))
    for agent in model.schedule.agents:
        if isinstance(agent, Robot):
            x, y = agent.pos
            grid[x][y] = 1
    return grid