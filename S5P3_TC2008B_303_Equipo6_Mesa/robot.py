# robot.py
from mesa.agent import Agent
from llegada import Llegada
from cargador import Cargador
import math
class Robot(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.ocupada = True
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.recarga = 0
        self.contiene = None
        self.destination = (0,0) #variable que almacenará el cargador al que se debe dirigir si su batería llega a un nivel crítico
        self.destino_paquete = None
        self.carga_optima = True 
        self.esta_cargando = False
        self.esta_esperando = True
        self.esta_recolectando = False 
        self.esta_almacenando = False
        self.esta_ofertando = False

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
        celda_a_limpiar.sucia = False
        self.sig_pos = celda_a_limpiar.pos

    def tomar_paquete(self):
        lista_tarima_llegada = [agent for agent in self.model.schedule.agents if isinstance(agent, Llegada)] #Arreglo de entrada para la lista de cargadores
        for tarima_llegada in lista_tarima_llegada:
            tipo_paquete = tarima_llegada.contiene
            self.contiene = tipo_paquete
            #funcion que define el detino_paquete a la posicion de la estanteria que corresponde
            self.destino_paquete = (5, 48)
            #libera la tarima
            tarima_llegada.liberar_tarima()

    def ir_a_estanteria(self):
        pass
    
    # cuando no tiene una celda sucia cerca se mueve de manera aleatoria (?)
    def seleccionar_nueva_pos(self, lista_de_vecinos):
        possible_pos = self.random.choice(lista_de_vecinos)
        while possible_pos.ocupada == True: # aqui nos aseguramos que al b|uscar una posición random no tome alguna ya ocupada
            possible_pos = self.random.choice(lista_de_vecinos)
        self.sig_pos = possible_pos.pos
    
    @staticmethod
    def distancia_euclidiana(punto1, punto2):
        x1, y1 = punto1
        x2, y2 = punto2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def comprobar_paquetes(self):
        #print(f'{self.unique_id} comprobando paquete...')
        lista_tarima_llegada = [agent for agent in self.model.schedule.agents if isinstance(agent, Llegada)] #Arreglo de entrada para la lista de cargadores
        for tarima_llegada in lista_tarima_llegada:
            #print('comprobando distancia')
            if tarima_llegada.sensor_paquete == True:
                distancia_a_llegada = self.distancia_euclidiana(self.pos, tarima_llegada.pos)
                if tarima_llegada.min_dist_recolector > distancia_a_llegada:
                    print(f'{self.unique_id} ofertando...')
                    tarima_llegada.min_dist_recolector = distancia_a_llegada
                    tarima_llegada.recolector_id = self.unique_id

    def recoger_paquete(self):
        lista_tarima_llegada = list()
        lista_tarima_llegada = [agent for agent in self.model.schedule.agents if isinstance(agent, Llegada)] #Arreglo de entrada para la lista de cargadores
        for tarima in lista_tarima_llegada:
            if tarima.recolector_id == self.unique_id:
                self.esta_recolectando = True
                self.esta_esperando = False
                self.destino_paquete = tarima.pos
                print(f'Robot {self.unique_id} escogido para recoger paquete')

    def ir_por_paquete(self):
        print(f'Robot {self.unique_id} yendo por paquete...')
        x_cargador, y_cargador = self.destino_paquete
        print(f"DESTINO: {self.destino_paquete}")

        # Dirigirse al cargador considerando al entorno
        vecinos = self.model.grid.get_neighbors(
                self.pos, moore=True, include_center=False)

        minDist = float('inf')
        for vecino in vecinos:
            dist = self.distancia_euclidiana(vecino.pos, self.destino_paquete)
            if dist < minDist:
                minDist = dist
                self.sig_pos = vecino.pos


    def buscar_cargador(self, origin):
        lista_cargadores = list()
        lista_cargadores = [agent for agent in self.model.schedule.agents if isinstance(agent, Cargador)] #Arreglo de entrada para la lista de cargadores
        minDistance = float('inf')
        closestCharger = None
        cargador_destino = None
        x, y = origin
        # Iterar sobre la lista de cargadores
        for cargador in lista_cargadores:
            cargador_pos = cargador.pos
            print(cargador.ocupada)
            distancia = self.distancia_euclidiana((x, y), cargador_pos)
            if abs(distancia) < abs(minDistance) and cargador.ocupada == False:
                minDistance = distancia
                closestCharger = cargador_pos
                cargador_destino = cargador
                d_x, d_y = closestCharger
                
        if cargador_destino != None:
            self.destination = (d_x, d_y)#Establecemos un destino para que el robot se dirija ahi
            cargador_destino.set_ocupada(True)
            self.esta_esperando = False
        # Si no encuentra cargador desocupado se detiene y entra en estado de espera
        if self.destination == (0, 0):
            self.esta_esperando = True
        # print(self.destination)


    def ir_a_cargador(self):
        # cambiarlo a que dentro de sus vecinos escoja la celda desocupada más cercana al cargador y se dirija hacia alla
        print("YENDO A CARGAR...")
        x_cargador, y_cargador = self.destination
        print(f"DESTINO: {self.destination}")
        
        # Dirigirse al cargador considerando al entorno
        vecinos = self.model.grid.get_neighbors(
                self.pos, moore=True, include_center=False)
        
        celdas = list()
        minDist = float('inf')
        for vecino in vecinos:
            dist = self.distancia_euclidiana(vecino.pos, self.destination)
            if dist < minDist:
                minDist = dist
                self.sig_pos = vecino.pos
        

        # print(f"SIGUIENTE PASO: {self.sig_pos}")
    
    def agentes_en_posicion(self, x, y):
        cell_contents = self.model.grid.get_cell_list_contents((x, y))
        return cell_contents
    
    def cargar_bateria(self):
        if self.carga > 90:
            x, y = self.pos  # Obtén la posición del agente principal
            celdas = self.model.grid.get_cell_list_contents([(x, y)])
            for contenido in celdas:
                if isinstance(contenido, Cargador):
                    # Modifica el atributo "ocupada" del Cargador
                    contenido.set_ocupada(False)
                    print(f"Se modificó 'ocupada' del Cargador en la posición {contenido.pos} a False")
                    
            self.carga_optima = True
            self.destination = (0,0)
            x, y = self.pos
            # agentes_en_celda = self.agentes_en_posicion(x, y)
            # cargador = [agent for agent in agentes_en_celda if isinstance(agent, Cargador)]
            # cargador[0].ocupada = False;    
        elif self.carga + 25 > 100:
            self.carga += 100 - self.carga
        else: 
            self.carga += 25
        
            
    def step(self):
        if self.carga > 25 and self.carga_optima:
            self.esta_cargando = False

            #En caso de que en el step anterior si haya habido un paquete en la banda, el robot define si ganó la subasta para ir por el paquete 
            if self.esta_ofertando == True:
                self.recoger_paquete()
                self.esta_ofertando = False

            #Este codigo se ejecuta siempre que el robot no esta ocupado, de manera que comprueba si no hay un paquete en la banda 
            if self.esta_esperando == True:
                self.comprobar_paquetes()
                self.esta_ofertando = True

            #Cuando un robot gana la subasta para recoger un paquete, se dirige hacia la traima de llegada
            if self.esta_recolectando == True and self.pos != self.destino_paquete:
                self.esta_esperando = False
                self.ir_por_paquete()

            #Una vez que el robot llega a la tarima de salida, entra en modo de almacenamiento, por lo que buscará la estantería correspondiente al articulo
            if self.esta_recolectando == True and self.pos == self.destino_paquete:
                self.esta_recolectando = False
                self.esta_almacenando = True
                self.tomar_paquete()
            
            if self.esta_almacenando == True and self.pos != self.destino_paquete:
                self.ir_por_paquete()
            
            if self.esta_almacenando == True and self.pos == self.destino_paquete:
                self.esta_esperando = True


        else: 
            self.carga_optima = False
            if self.destination == (0,0):
                print("BATTERY RUNNING OUT!")
                self.buscar_cargador(self.pos)
            elif self.destination != (0,0) and self.pos != self.destination: 
                self.ir_a_cargador()
            else:
                self.esta_cargando = True
                self.cargar_bateria()
                self.recarga += 1
                print(f"Cantidad de recargas: {self.recarga}")


    def advance(self):
        # En caso de querer meter una negociación con otros agentes, se debería de colocar aqui
        if self.esta_esperando == False:
            if self.pos != self.sig_pos:
                self.movimientos += 1

        if self.carga > 0:
            if self.esta_cargando == False and self.esta_esperando == False:
                self.carga -= 0.5
                self.model.grid.move_agent(self, self.sig_pos)