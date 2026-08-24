capacete = input("Está utilizando capacete? (S/N)")
oculos = input("Está utilizando óculos de proteção? (S/N)")
auricular = input("Está utilizando protetor auricular? (S/N)")
calcado = input("Está utilizando calçado de segurança? (S/N)")

if capacete == "S" and oculos == "S" and auricular == "S" and calcado == "S" :
    print("Acesso liberado para atividade")
else :
    print("Atenção: verifique os EPIs antes de iniciar a atividade")