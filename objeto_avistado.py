from numpy import ndarray, multiply, zeros, count_nonzero

TRADUCAO = {
    'human': 'humano',
    'hand': 'mao',
    'cell phone': 'celular',
    'banana': 'banana',
    'apple': 'maca',
    'fork': 'garfo',
    'bottle': 'garrafa',
    'person': 'humano',
    'cell phone': 'celular',
    'traffic light': 'sinaleiro',
    'knife': 'faca',
    'donut': 'maca',
    'chair': 'cadeira',
    'laptop': 'notebook',
    'keyboard': 'teclado',
    'mouse': 'mouse',
    #Saidas do Google
    'Man': 'humano',
    'Person': 'humano',
    'Banana': 'banana',
    'Apple': 'maca',
    'Bottle': 'garrafa',
    'Mobile phone': 'celular'
}

#TODO: classe meio inútil. Pensar em talvez incluir apenas coordenadas aqui
class DistanciaCartesiana:

    def __init__(self, x, y):
        self.delta_x = x
        self.delta_y = y

    def horizontal(self):
        raise NotImplemented
        # TODO: retornar algum texto ou algo de facil manuseio para ser transformado em audio

    def vertical(self):
        raise NotImplemented
        # TODO: idem ao anterior


# noinspection PyBroadException
class ObjetoAvistado:
    """
    Classe representa um objeto visto pela camera e reconhecido pelo opencv.
    """


    def __init__(self, saida_opencv: tuple):
        """
        :param saida_opencv: uma tupla contendo as coordenadas do quadro, e o nome em ingles do objeto na seguinte
        ordem: (x1, y1, x2, y2, nome).
        """
        self.nome_ingles = saida_opencv[-1]
        try:
            self.nome = TRADUCAO[self.nome_ingles]
        except:
            self.nome = 'unknown'
            print(self.nome_ingles)
        self.x_1 = saida_opencv[0]
        self.y_1 = saida_opencv[1]
        self.x_2 = saida_opencv[2] + self.x_1
        self.y_2 = saida_opencv[3] + self.y_1
        self.x, self.y = self.centro
        self.modo_vertical = True
        self.modo_horizontal = False
        self._fazer_matriz()

    def __lt__(self, other) -> bool:
        """
        Depende do modo em que a instancia de comparacao esta setada. No modo horizontal, me diz se o objeto esta mais
        a direita ou esquerda. No modo vertical, me diz se o objeto esta mais acima ou abaixo do segundo.
        :param other:
        :return:
        """
        if self.modo_horinzontal:
            return self.x < other.x
        else:
            return self.y < other.y

    def __sub__(self, other) -> DistanciaCartesiana:
        """
        Subtracao significa a diferenca, ou seja, distancia de um objeto para o outro.
        :param other: outro objeto avistado.
        :return: uma distancia cartesiana.
        """
        return DistanciaCartesiana(self.x - other.x, self.y - other.y)

    def __str__(self):
        return self.nome

    def _fazer_matriz(self):
        """
        Crio a matriz de pixels para este objeto. Isso será usado posteriormente para verificar se um objeto está
        sobreposto ao outro.
        :return:
        """
        MAX = 1000
        self.matriz_pixels = zeros((MAX, MAX), dtype=int)
        for i in range(MAX):
            for j in range(MAX):
                if self.x_1 < i < self.x_2 and self.y_1 < j < self.y_2:
                    self.matriz_pixels[i, j] = 1

    def sobrepoe(self, other) -> bool:
        """
        Me diz se o primeiro está sobreposto ao outro, mesmo que parcialmente.
        :param other: o outro objeto de comparação.
        :return: se está sobrepondo.
        """
        resultado = multiply(self.matriz_pixels, other.matriz_pixels)
        return count_nonzero(resultado) != 0

    def esta_acima(self, other):
        return self.centro[0] > other.centro[0]

    def esta_esquerda(self, other):
        return self.centro[1] < other.centro[1]

    @property
    def centro(self) -> tuple:
        """
        Calcula o epicentro do objeto. Transforma um quadro em um ponto.
        :return: uma tupla de 2 termos contendo as coordenadas x e y
        """
        return (self.x_1 + self.x_2) / 2, (self.y_1 + self.y_2) / 2


