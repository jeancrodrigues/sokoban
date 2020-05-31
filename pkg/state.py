class State:
    """Representa um estado do problema.
    Neste caso, é um par ordenado que representa a linha e a coluna onde se encontra o agente no labirinto."""

    def __init__(self, row, col, boxes):
        self.row = row
        self.col = col
        self.boxes = boxes
        self.boxes.sort()

    def __eq__(self, other):
        sum = 0
        for box in self.boxes:
            for otherbox in other.boxes:
                if box == otherbox:
                    sum += 1
        return sum == len(other.boxes)

    def __str__(self): 
        # Permite fazer um print(state) diretamente
        return "({0:d}, {1:d})".format(self.row, self.col)