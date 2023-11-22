from mesa.agent import Agent

class Salida(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.ocupada = False
        self.sensor_paquete = False #Define si llegó un tipo de paquete
        self.pide = None #Tipo de paquete que llegó 
