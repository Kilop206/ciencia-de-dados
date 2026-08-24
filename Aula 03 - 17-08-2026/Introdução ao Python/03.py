def aprovadas(total, aprovadas, reprovadas):
    print("Peças produzidas: ", total)
    print("Peças aprovadas: ", aprovadas)
    print("Peças reprovadas: ", reprovadas)
    print("Percentual de aprovação: ", (aprovadas / total * 100))

aprovadas(10, 5, 5)