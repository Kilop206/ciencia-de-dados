import sys

from Colaborador import Colaborador

colaboradores = []

def cadastrar_colaborador():
    nome = input("Insira o nome do colaborador: ")
    matricula = input("Insira a matrícula do colaborador: ")
    setor = input("Insira o setor do colaborador: ")
    cargo = input("Insira o cargo do colaborador: ")
    
    colaborador = Colaborador(nome, matricula, setor, cargo)
    colaboradores.append(colaborador)

def listar_colaboradores() :
    for c in colaboradores :
        print(c.__str__())

def pesquisar_colaborador_por_matricula(matricula) :
    for c in colaboradores :
        if c.matricula == matricula :
            print(c.__str__())

def colaboradores_por_setor() :
    setores = {}
    for c in colaboradores :
        if c.setor not in setores :
            setores[c.setor] = 1
        else :
            setor = setores.get(c.setor)
            setores[c.setor] = setor + 1
    
    print(setores)

while (True) :
    escolha = int(input("""1. Cadastrar colaborador
2. Listar colaboradores
3. Pesquisar colaborador pela matrícula
4. Mostrar quantos colaboradores existem em cada setor
0. Sair
Faça sua escolha: """))
    
    match escolha :
        case 1 :
            cadastrar_colaborador()
        case 2 :
            listar_colaboradores()
        case 3 :
            matricula = input("Insira a matricula do colaborador: ")
            pesquisar_colaborador_por_matricula(matricula)
        case 4 :
            colaboradores_por_setor()
        case 0 : 
            sys.exit(0)