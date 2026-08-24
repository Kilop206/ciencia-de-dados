import sys

from Colaborador import Colaborador
from Maquina import Maquina
from Producao import Producao
from InspecaoQualidade import InspecaoQualidade

colaboradores = []
maquinas = []
producoes = []
inspecoes_qualidade = []

def procurar_maquina(matricula: str) :
    for m in maquinas :
        if m.matricula == matricula :
            return m
    else :
        print("Máquina não encontrada")
        return None
    

def cadastrar_colaborador():
    nome = input("Insira o nome do colaborador: ")
    matricula = input("Insira a matrícula do colaborador: ")
    setor = input("Insira o setor do colaborador: ")
    cargo = input("Insira o cargo do colaborador: ")
    
    colaborador = Colaborador(nome, matricula, setor, cargo)
    colaboradores.append(colaborador)


def cadastrar_maquina():
    nome = input("Insira o nome da maquina: ")
    matricula = input("Insira a matrícula da maquina: ")
    setor = input("Insira o setor da maquina: ")
    qtd = input("Insira a quantidade de peças produzidas pela máquina: ")
    
    maquina = Maquina(nome, matricula, setor, qtd)
    maquinas.append(maquina)


def registrar_producao() :
    peca = input("Insira o nome da peça: ")
    qtd = input("Insira a quantidade de peças produzidas: ")

    producao = Producao(peca, qtd)
    producoes.append(producao)


def registrar_inspecao_qualidade() :
    matricula = input("Insira a matrícula da maquina: ")

    maquina: Maquina = procurar_maquina(matricula)

    status = input("Insira o status da maquina: ")
    
    inspecao_qualidade = InspecaoQualidade.__init__(maquina, status)
    maquinas.append(inspecao_qualidade)

def consultar_producao(peca) :
    for p in producoes :
        if p.peca == peca :
            print(p.__str__())


def relatorio_producao() :
    for c in colaboradores :
        print(c.__str__())
    for m in maquinas :
        print(m.__str__())
    for p in producoes :
        print(p.__str__())
    for i in inspecoes_qualidade :
        print(i.__str__())
        

while (True) :
    escolha = int(input("""1 - Cadastrar colaborador
2 - Cadastrar máquina
3 - Registrar produção
4 - Registrar inspeção de qualidade
5 - Consultar produção
6 - Relatório da produção
0 - Sair"""))
    
    match escolha :
        case 1 :
            cadastrar_colaborador()
        case 2 :
            cadastrar_maquina()
        case 3 :
            registrar_producao()
        case 4 :
            registrar_inspecao_qualidade()
        case 5 :
            matricula = input("Insira o nome da peça: ")
            consultar_producao(matricula)
        case 6 :
            relatorio_producao()
        case 0 :
            sys.exit(0)