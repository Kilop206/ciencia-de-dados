a = 10
b = 1.2
c = "nome"
d = True

nome = input("Insira o seu nome: ")
print(nome)

idade = int(input("Insira sua idade: "))
print(idade)

altura = float(input("Insira sua altura: "))
print(altura)

print(len(nome)) # Conta o número de letras numa string
print(nome.capitalize()) # Faz a primeira letra se tornar maiúscula e as outras minúsculas
print(nome.count("a")) # Conta quantas vezes a letra aparece
print(nome.startswith("a")) # Verifica se começa com a letra
print(nome.endswith("a")) # Verifica se termina com a letra
print(nome.isalnum()) # Verifica se contém conteúdo alfanumérico
print(nome.isalpha()) # Verifica se contém conteúdo alfabético
print(nome.islower()) # Verifica se todas as letras são minúsculas
print(nome.isupper()) # Verifica se todas as letras são maiúsculas
print(nome.swapcase()) # Inverte o conteúdo da string (Minúsculo / Maiúsculo)
print(nome.title()) # Converte para maiúsculo todas as primeiras letras de cada palavra da string
print(nome.split()) # Transforma a string em uma lista, utilizando os espaços como referência
print(nome.replace("", " Döge")) # Substitui na string o trecho S1 pelo trecho S2.
print(nome.find("a")) # Retorna o índice da primeira ocorrência de um determinado caractere na string. Se o caractere não estiver na string retorna -1
print(nome.ljust(15)) # Ajusta a string para um tamanho mínimo, acrescentando espaços à direita se necessário
print(nome.rjust(15)) # Ajusta a string para um tamanho mínimo, acrescentando espaços à esquerda se necessário.
print(nome.center(10)) # Ajusta a string para um tamanho mínimo, acrescentando espaços à esquerda e à direita, se necessário
print(nome.lstrip()) # Remove todos os espaços em branco do lado esquerdo da string
print(nome.rstrip()) # Remove todos os espaços em branco do lado direito da string
print(nome.strip()) # Remove todos os espaços em branco da string

A = "Um elefante incomoda muita gente"
print(A[3:20])

B = input("Insira uma frase: ")
print(B.upper().replace(" ", ""))

x = int(input("Primeiro número: "))
y = int(input("Segundo número: "))

z = ((x ** 2) + (y ** 2)) / ((x - y) ** 2)
print(z)

salario = float(input("Insira o salário: "))
print(salario + (salario / 100 * 35))

L = [5, 7, 2, 9, 4, 1, 3]

print(len(L))
print(max(L))
print(min(L))
print(sum(L))
print(sorted(L))
print(sorted(L, reverse=True))

L1 = range(3, 51, 3)
print(list(L1))

# Tuplas são imutáveis

tupla = (1, 2, 3, 4, 5, 6, 7, 8, 9, 0)

# Dicionários

dicionario = {"chave1": 1, "chave2": 2, "chave3": 3}

dicionario["chave4"] = 4

print(dicionario)

del dicionario["chave4"]

print("chave3" in dicionario)
print("chave4" in dicionario)

print(dicionario.keys())
print(dicionario.values())

lanchonete = {"salgado": 4.5, "lanche": 6.5 , "suco": 3.0, "refrigerante": 3.5, "doce": 1.0}

alunos = {"aluno1": 9, "aluno2": 8, "aluno3": 7, "aluno4": 6, "aluno5": 5}

media = 0
for i in alunos :
    media += alunos[i]
    
print(media)

nota1 = float(input("Nota 1: "))
nota2 = float(input("Nota 2: "))

media = (nota1 + nota2) / 2

if media >= 6 :
    print("Aprovado!")
else :
    print("Reprovado!")

if media > 6 :
    print("Aprovado!")
elif media < 4:
    print("Reprovado!")
else :
    print("Exame!")

S = 0
for i in range(3, 334, 3) :
    S += i
print(S)

notas = [1,2,3,4,5,6,7,8,9,10]
soma = 0
for i in notas :
    soma += i
print(soma / len(notas))

numero = None

while numero not in notas :
    numero = float(input("Insira um número de 1 a 10: "))

for i in notas :
    print(numero * i)

def desenhar_linha(tamanho: int) :
    for i in range(0, tamanho, 1) :
        print("_", end="")

desenhar_linha(5)

def imprimir_lista(lista) :
    index = 0
    for i in lista :
        print(index, ": ", i)
        index += 1

imprimir_lista([1,2,3,4,5,6,6,7,8,9,0])

def media_lista(lista: list) :
    return sum(lista) / len(lista)

print(media_lista([1,32,3,4,5,6,7,8,9,0]))