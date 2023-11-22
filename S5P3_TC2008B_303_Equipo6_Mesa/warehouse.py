from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from typing import List, Dict
from robot import Robot
from cargador import Cargador
from llegada import Llegada
from salida import Salida
from estanteria import Estanteria
from celda import Celda
import json
import numpy as np

class Warehouse(Model):
    # Initialize Grid
    def __init__(self, width: int, height: int,
                    num_agentes: int = 5,
                    porc_celdas_sucias: float = 0.6,
                    porc_muebles: float = 0.1,
                    modo_pos_inicial: str = 'Fija',
                    time: int = 0,
                    num_cuadrantesX: int = 2, 
                    num_cuadrantesY: int = 2
                    ):
        
        # Initialize variables 
        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        self.num_cuadrantesX = num_cuadrantesX
        self.num_cuadrantesY = num_cuadrantesY
        self.time = time
        
        # Initialize MultiGrid
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        
        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        for id, pos in enumerate(posiciones_disponibles):
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, False)
            self.grid.place_agent(celda, pos)

        # Posicionamiento de tarima de llegada 
        tarima_llegada = Llegada("Llegada", self)
        self.grid.place_agent(tarima_llegada, (44, 48))
        self.schedule.add(tarima_llegada)

        # Posicionamiento de la tarima de salida
        tarima_salida = Salida("Salida", self)
        self.grid.place_agent(tarima_salida, (5, 48) )
        self.schedule.add(tarima_salida)

        # Posicionamiento de robots
        posicion_inicial = 49
        cambio_en_posicion = 1
        for id in range(num_agentes):
            robot = Robot(id, self)
            self.grid.place_agent(robot, (posicion_inicial, 46))
            posicion_inicial = posicion_inicial - cambio_en_posicion
            if posicion_inicial == 44:
                posicion_inicial = 0
                cambio_en_posicion = -1
            self.schedule.add(robot)

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid, "Cargas": get_cargas},
        )
        
        # Posicionamiento de cargadores
        ubicaciones_cargadores_x = {23, 24, 25, 26, 27, 28}
        for pos in ubicaciones_cargadores_x:
            cargador = Cargador(f"{pos}", self)
            self.schedule.add(cargador)
            self.grid.place_agent(cargador, (pos, 49))

         # Posicionamiento de estanterias
        ubicacion_estanterias_x = {8, 16, 35, 43}
        ubicacion_estanterias_y = {10, 20, 30, 40}
        for pos_x in ubicacion_estanterias_x:
            for pos_y in ubicacion_estanterias_y:
                estanteria = Estanteria(f"Estanteria_{pos_x}_{pos_y}", self)
                self.schedule.add(estanteria)
                self.grid.place_agent(estanteria, (pos_x, pos_y))


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
        self.running = True
        self.datacollector.collect(self)
        self.schedule.step()
        self.time += 1

def get_grid(model: Model) -> np.ndarray:
    """
    Método para la obtención de la grid y representarla en un notebook
    :param model: Modelo (entorno)
    :return: grid
    """
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, Robot):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid

def get_cargas(model: Model):
    return [(agent.unique_id, agent.carga) for agent in model.schedule.agents if isinstance(agent, Robot)]

def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, Robot):
        return {agent.unique_id: agent.movimientos}