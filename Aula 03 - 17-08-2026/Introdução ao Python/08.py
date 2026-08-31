producao = [850, 920, 880, 1050, 990]

def producao_diaria(producao) :
    return [
        sum(producao),
        sum(producao) / len(producao),
        max(producao),
        min(producao)
    ]

print(producao_diaria(producao))