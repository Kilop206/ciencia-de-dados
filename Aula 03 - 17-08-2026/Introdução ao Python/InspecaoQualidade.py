import datetime

from Maquina import Maquina

class InspecaoQualidade : 
    def __init__(self, maquina: Maquina, status: str) :
        self.maquina = maquina
        self.status = status
        self.data = datetime.datetime.now()

    def __str__(self) :
        return "Máquina: " + self.maquina.matricula + "\nStatus: " + self.status  + "\nData: " + self.data