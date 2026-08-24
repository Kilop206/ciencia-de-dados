from Colaborador import Colaborador

nome = input("Insira o nome: ")
matricula = input("Insira a matrícula: ")
setor = input("Insira o setor: ")
cargo = input("Insira o cargo: ")

colaborador = Colaborador.__init__(nome, matricula, setor, cargo)

print(colaborador.__str__())