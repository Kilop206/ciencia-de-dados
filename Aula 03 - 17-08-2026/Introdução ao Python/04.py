materiais_quantidades = {"Parafuso": 5, "Cabo": 30, "Rolamento": 8, "Terminal": 50}

for i in materiais_quantidades :
    print(materiais_quantidades[i] < 10 if "Em falta" else "Em estoque")