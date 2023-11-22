from mesa.agent import Agent

class Estanteria(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.ocupada = True
        self.contenido = 0
    
    def pos_estanteria(i, j):
        pos_x = i
        pos_y = j
        return pos_x, pos_y