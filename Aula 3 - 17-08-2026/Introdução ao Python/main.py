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