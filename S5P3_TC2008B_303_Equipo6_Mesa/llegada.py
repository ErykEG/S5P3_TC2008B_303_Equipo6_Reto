from mesa.agent import Agent

class Llegada(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.ocupada = False
        self.sensor_paquete = False #Define si llegó un tipo de paquete
        self.contiene = 0 #Tipo de paquete que llegó 
        self.recolector_id = None #Id del robot que esta más cerca del paquete que llegó y recogerá el paquete 
        self.min_dist_recolector = float('inf') #Variable que decidirá quien va por el paquete mediante un proceso de subasta por distancia 
        self.paquetes_por_llegar = [1, 2, 3, 4] #Arreglo que contendrá la cantidad y tipo de paquete que irá llegando x steps {tipo:step}
        self.horas_de_llegada = [10, 50, 100, 200]
        self.paso = 0

    def step(self):
        self.paso += 1

    def advance(self):
        if self.paso in self.horas_de_llegada:
            print('----Llamada de paquete entrante----')
            self.horas_de_llegada.remove(self.paso)  # Remover el paso actual de las horas de llegada
            self.contiene = self.paquetes_por_llegar.pop(0)  # Remover y obtener el primer paquete de la lista
            self.sensor_paquete = True
        

    def liberar_tarima(self):
        self.sensor_paquete = False
        self.contiene = None
        self.recolector_id = None
        self.min_dist_recolector = float('inf')