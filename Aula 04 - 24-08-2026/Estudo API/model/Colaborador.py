class Colaborador:
    def __init__(self, nome: str, matricula: str, setor: str, cargo: str):
        self.nome = nome
        self.matricula = matricula
        self.setor = setor
        self.cargo = cargo
    
    def __str__(self):
        return "Nome: " + self.nome + "\nMatricula: " + self.matricula + "\nSetor: " + self.setor + "\nCargo: " + self.cargo