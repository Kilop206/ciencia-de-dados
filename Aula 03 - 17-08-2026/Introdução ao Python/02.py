producoes = []

for i in range(1, 6):
    valor = float(input(f"Insira a produção do dia {i}: "))
    producoes.append(valor)

print(sum(producoes))
print(sum(producoes) / len(producoes))
print(max(producoes))