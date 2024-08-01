class Piece:
    def __init__(self,tipo,colore,posizione,vita=1,attacco=1,nmosse=1):
        self.tipo=tipo
        self.vita=vita
        self.attacco=attacco
        self.nmosse=nmosse
        self.colore=colore
        self.posizione=posizione

    def __str__(self):
        return f"{self.tipo[0].upper()}{self.colore[0].upper()}"  # Rappresenta il pezzo con le prime lettere di colore e tipo
