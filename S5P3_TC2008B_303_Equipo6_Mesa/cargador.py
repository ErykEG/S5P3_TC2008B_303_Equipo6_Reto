from mesa.agent import Agent

# Agente cargador
class Cargador(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carga = 100
        self.ocupada = False
    
    def set_ocupada(self, value):
        self.ocupada = value
