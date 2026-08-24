class Maquina:
    def __init__(self, nome: str, matricula: str, setor: str, pecas_produzidas: int):
        self.nome = nome
        self.matricula = matricula
        self.setor = setor
        self.pecas_produzidas = pecas_produzidas
    
    def __str__(self):
        return "Nome: " + self.nome + "\nMatricula: " + self.matricula + "\nSetor: " + self.setor + "\nPeças Produzidas: " + self.pecas_produzidas