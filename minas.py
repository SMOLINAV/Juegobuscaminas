# Importar todo lo necesario
from collections import deque
from tkinter import *
from tkinter import messagebox as tkMessageBox
import random
import platform
from datetime import datetime

# Definir constantes

# Tamaño del tablero
TAM_X = 10
TAM_Y = 10

# Estados de las celdas
ESTADO_POR_DEFECTO = 0
ESTADO_PULSADO = 1
ESTADO_BANDERA = 2

# Eventos de los botones
BTN_PULSAR = "<Button-1>"
BTN_BANDERA = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

# Crear ventana principal
ventana = None

# Definir clase buscaminas
class Buscaminas:
    """ Clase buscaminas

    Crea el tablero de juego y tiene la logica del juego
    """

    def __init__(self, tk):
        """ 
        Crea el tablero de juego
        Args:
            tk (Tk) - ventana principal
        Returns: 
            None
        """

        # Importar imágenes para las celdas
        self.imagenes = {
            "normal": PhotoImage(file = "images/tile_plain.gif"),
            "pulsado": PhotoImage(file = "images/tile_clicked.gif"),
            "mina": PhotoImage(file = "images/tile_mine.gif"),
            "bandera": PhotoImage(file = "images/tile_flag.gif"),
            "incorrecta": PhotoImage(file = "images/tile_wrong.gif"),
            "numeros": []
        }
        for i in range(1, 9):
            self.imagenes["numeros"].append(PhotoImage(file = "images/tile_"+str(i)+".gif"))

        # Configurar el marco de la ventana
        self.tk = tk
        self.marco = Frame(self.tk)
        self.marco.pack()

        # Configurar etiquetas
        self.etiquetas = {
            "tiempo": Label(self.marco, text = "00:00:00"),
            "minas": Label(self.marco, text = "Minas: 0"),
            "banderas": Label(self.marco, text = "Banderas: 0")
        }

        # Colocar las etiquetas en la ventana
        self.etiquetas["tiempo"].grid(row = 0, column = 0, columnspan = TAM_Y)
        self.etiquetas["minas"].grid(row = TAM_X+1, column = 0, columnspan = int(TAM_Y/2))
        self.etiquetas["banderas"].grid(row = TAM_X+1, column = int(TAM_Y/2)-1, columnspan = int(TAM_Y/2))

        # Iniciar el juego
        self.reiniciar()

        # Iniciar temporizador
        self.actualizarTemporizador() 

    def configurar(self):
        """
        Crea el tablero de juego
        Args:
            None
        Returns: 
            None
        """

        # Crear variables de banderas y celdas pulsadas
        self.contadorBanderas = 0
        self.contadorBanderasCorrectas = 0
        self.contadorPulsadas = 0
        self.tiempoInicio = None

        # Crear botones para el tablero
        self.celdas = dict({})
        self.minas = 0
        for x in range(0, TAM_X):
            for y in range(0, TAM_Y):
                if y == 0:
                    self.celdas[x] = {}

                id = str(x) + "_" + str(y)
                esMina = False

                # Imagen de celda modificable por razones de depuración:
                gfx = self.imagenes["normal"]

                # Generar minas aleatoriamente
                if random.uniform(0.0, 1.0) < 0.1:
                    esMina = True
                    self.minas += 1

                # Crear celda con su respectivo botón
                celda = {
                    "id": id,
                    "esMina": esMina,
                    "estado": ESTADO_POR_DEFECTO,
                    "coordenadas": {
                        "x": x,
                        "y": y
                    },
                    "boton": Button(self.marco, image = gfx),
                    "minas": 0
                }

                celda["boton"].bind(BTN_PULSAR, self.alPulsar(x, y))
                celda["boton"].bind(BTN_BANDERA, self.alClicDerecho(x, y))
                celda["boton"].grid( row = x+1, column = y )

                self.celdas[x][y] = celda

        # Calcular la cantidad de minas por celda
        for x in range(0, TAM_X):
            for y in range(0, TAM_Y):
                mc = 0
                for n in self.obtenerVecinos(x, y):
                    mc += 1 if n["esMina"] else 0
                self.celdas[x][y]["minas"] = mc


    def reiniciar(self):
        """
        Reinicia el juego
        Args:
            None
        Returns: 
            None
        """
        self.configurar()
        self.actualizarEtiquetas()


    def actualizarEtiquetas(self):
        '''
        Actualiza las etiquetas de tiempo, banderas y minas
        Args:
            None
        Returns: 
            None
        '''
        self.etiquetas["tiempo"].config(text = "00:00:00")
        self.etiquetas["minas"].config(text = "Minas: "+str(self.minas))
        self.etiquetas["banderas"].config(text = "Banderas: "+str(self.contadorBanderas))
        self.etiquetas["minas"].config(text = "Minas: "+str(self.minas))


    def finJuego(self, ganado):
        '''
        Finaliza el juego
        Args:
            None
        Returns: 
            None
        '''
        for x in range(0, TAM_X):
            for y in range(0, TAM_Y):
                if self.celdas[x][y]["esMina"] == False and self.celdas[x][y]["estado"] == ESTADO_BANDERA:
                    self.celdas[x][y]["boton"].config(image = self.imagenes["incorrecta"])
                if self.celdas[x][y]["esMina"] == True and self.celdas[x][y]["estado"] != ESTADO_BANDERA:
                    self.celdas[x][y]["boton"].config(image = self.imagenes["mina"])

        self.tk.update()


        # Mostrar mensaje de fin de juego
        msg = "¡Has ganado! ¿Jugar de nuevo?" if ganado else "¡Has perdido! ¿Jugar de nuevo?"
        res = tkMessageBox.askyesno("Fin del juego", msg)
        if res:
            self.reiniciar()
        else:
            self.tk.quit()


    def actualizarTemporizador(self):
        '''
        Actualiza el temporizador
        Args:
            None
        Returns: 
            None
        '''
        ts = "00:00:00"
        if self.tiempoInicio != None:
            delta = datetime.now() - self.tiempoInicio
            ts = str(delta).split('.')[0]
            if delta.total_seconds() < 36000:
                ts = "0" + ts
        
        # Actualizar etiquetas
        self.etiquetas["tiempo"].config(text = ts)

        # Repetir hasta que se acabe el tiempo
        self.marco.after(100, self.actualizarTemporizador)


    def obtenerVecinos(self, x, y):
        '''
        Obtiene los vecinos de una celda
        Args:
            x (int) - coordenada x de la celda
            y (int) - coordenada y de la celda
        Returns: 
            list - lista de celdas vecinas
        '''
        vecinos = []
        coordenadas = [
            {"x": x-1,  "y": y-1},  # arriba derecha
            {"x": x-1,  "y": y},    # arriba medio
            {"x": x-1,  "y": y+1},  # arriba izquierda
            {"x": x,    "y": y-1},  # izquierda
            {"x": x,    "y": y+1},  # derecha
            {"x": x+1,  "y": y-1},  # abajo derecha
            {"x": x+1,  "y": y},    # abajo medio
            {"x": x+1,  "y": y+1},  # abajo izquierda
        ]
        for n in coordenadas:
            try:
                vecinos.append(self.celdas[n["x"]][n["y"]])
            except KeyError:
                pass
        return vecinos


    def alPulsar(self, x, y):
        '''
        Al pulsar una celda
        Args:
            x (int) - coordenada x de la celda
            y (int) - coordenada y de la celda
        Returns: 
            lambda Boton - lambda que ejecuta la pulsación de la celda
        '''
        return lambda Boton: self.pulsarCelda(self.celdas[x][y])


    def alClicDerecho(self, x, y):
        '''
        Al pulsar una celda
        Args:
            x (int) - coordenada x de la celda
            y (int) - coordenada y de la celda
        Returns: 
            lambda Boton - lambda que ejecuta la pulsación de la celda
        '''
        return lambda Boton: self.clicDerecho(self.celdas[x][y])


    def pulsarCelda(self, celda):
        '''
        Pulsar una celda
        Args:
            celda (dict) - celda pulsada
        Returns: 
            None
        '''
        if self.tiempoInicio == None:
            self.tiempoInicio = datetime.now()

        if celda["esMina"] == True:

            # Fin del juego
            self.finJuego(False)
            return

        # Cambiar imagen
        if celda["minas"] == 0:
            celda["boton"].config(image = self.imagenes["pulsado"])
            self.despejarCeldasVecinas(celda["id"])
        else:
            celda["boton"].config(image = self.imagenes["numeros"][celda["minas"]-1])

        # Si aún no está marcada como pulsada, cambiar estado y contar
        if celda["estado"] != ESTADO_PULSADO:
            celda["estado"] = ESTADO_PULSADO
            self.contadorPulsadas += 1
        if self.contadorPulsadas == (TAM_X * TAM_Y) - self.minas:
            self.finJuego(True)


    def clicDerecho(self, celda):
        '''
        Al pulsar una celda
        Args:
            celda (dict) - celda pulsada
        Returns: 
            None
        '''
        if self.tiempoInicio == None:
            self.tiempoInicio = datetime.now()

        # Si la celda no está pulsada
        if celda["estado"] == ESTADO_POR_DEFECTO:
            celda["boton"].config(image = self.imagenes["bandera"])
            celda["estado"] = ESTADO_BANDERA
            celda["boton"].unbind(BTN_PULSAR)

            # Si es una mina
            if celda["esMina"] == True:
                self.contadorBanderasCorrectas += 1
            self.contadorBanderas += 1
            self.actualizarEtiquetas()

        # Si está marcada, desmarcar con una bandera
        elif celda["estado"] == ESTADO_BANDERA:
            celda["boton"].config(image = self.imagenes["normal"])
            celda["estado"] = ESTADO_POR_DEFECTO
            celda["boton"].bind(BTN_PULSAR, self.alPulsar(celda["coordenadas"]["x"], celda["coordenadas"]["y"]))
            # si es una mina
            if celda["esMina"] == True:
                self.contadorBanderasCorrectas -= 1
            self.contadorBanderas -= 1
            self.actualizarEtiquetas()


    def despejarCeldasVecinas(self, id):
        '''
        Despejar celdas vecinas
        Args:
            id (str) - identificador de la celda
        Returns: 
            None
        '''
        cola = deque([id])

        while len(cola) != 0:
            clave = cola.popleft()
            partes = clave.split("_")
            x = int(partes[0])
            y = int(partes[1])

            for celda in self.obtenerVecinos(x, y):
                self.despejarCelda(celda, cola)


    def despejarCelda(self, celda, cola):
        '''
        Despejar una celda
        Args:
            celda (dict) - celda a despejar
            cola (deque) - cola de celdas
        Returns: 
            None
        '''
        if celda["estado"] != ESTADO_POR_DEFECTO:
            return

        if celda["minas"] == 0:
            celda["boton"].config(image = self.imagenes["pulsado"])
            cola.append(celda["id"])
        else:
            celda["boton"].config(image = self.imagenes["numeros"][celda["minas"]-1])

        celda["estado"] = ESTADO_PULSADO
        self.contadorPulsadas += 1


### FIN DE CLASES ###

def principal():
    '''
    Función principal
    Args:
        None
    Returns: 
        None
    '''
    ventana = Tk()
    
    # Establecer título del programa
    ventana.title("Buscaminas")

    # Crear instancia del juego
    buscaminas = Buscaminas(ventana)

    # Ejecutar bucle de eventos
    ventana.mainloop()

if __name__ == "__main__":
    principal()

