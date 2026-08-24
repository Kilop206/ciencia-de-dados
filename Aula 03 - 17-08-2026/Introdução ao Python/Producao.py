class Producao :
    def __init__(self, peca: str, quantidade: int) :
        self.peca = peca
        self.quantidade = quantidade

    def __str__(self) :
        return "Peça" + self.peca + "\nQuantidade: " + self.quantidade