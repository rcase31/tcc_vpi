from reconhecimento_audio import *
from reconhecimento_video import *
from reproducao_audio import *
from objeto_avistado import *
from enum import Enum


class Estado(Enum):
    ESPERA = 0
    LEITURA = 1
    AGUARDA_OBJETO = 2
    ORIENTACAO = 3
    OBJETO_ENCONTRADO = 4

    def proximo(self):
        return Estado(self.value + 1)


# noinspection PyBroadException
class Assistente:


    def __init__(self):
        self.estado = Estado.ESPERA
        self.fala = PlayerAudio()
        self.olhos = ReconhecedorObjetos()
        self.objeto_em_mira = None

    def procura_objetos(self):
        with self.olhos:
            # aqui eu recebo o seguinte formato: ((x1, y1, x2, y2, mao), (objeto_1, objeto_2,..., objeto_n))
            coordenadas_mao, coordenadas_objetos = self.olhos.procurar_c_insistencia(quantidade_maxima=2)
            if len(coordenadas_objetos) == 0 or coordenadas_mao is None:
                return False
            self.mao = ObjetoAvistado(coordenadas_mao)
            self.objetos = [ObjetoAvistado(obj) for obj in coordenadas_objetos]
            return True

    def reproduz_fala(self, audio: str):
        self.fala.play(audio)

    def avanca_estado(self):
        self.estado = self.estado.proximo()

    def volta_para_estado_inicial(self):
        self.estado = Estado.ESPERA
        
    def mira_em_primeiro_objeto(self):
        self.objeto_em_mira = self.objetos[0]

    def direciona(self) -> bool:
        """
        :return: retorna verdadeiro quando o objeto desejado estiver alinhado com a mão.
        """
        # Atualizo a posição da mão
        coordenadas_mao = self.olhos.atualiza_pos_mao()
        if coordenadas_mao is None:
            self.fala.play(Audio.NAO_VEJO_MAO)
            return False
        else:
            self.mao = ObjetoAvistado(coordenadas_mao)
        # Checa se a posição da mão sobrepõe o objeto (aqui eu assumo o objeto como estático)
        if self.mao.sobrepoe(self.objeto_em_mira):
            #self.fala.play(Audio.OBJETO_EM_MIRA)
            return True
        else:
            if self.mao.esta_esquerda(self.objeto_em_mira):
                self.fala.play(Audio.ESQUERDA)
            else:
                self.fala.play(Audio.DIREITA)
            if self.mao.esta_acima(self.objeto_em_mira):
                self.fala.play(Audio.ABAIXO)
            else:
                self.fala.play(Audio.ACIMA)
            return False

    def retorna_objetos_vistos(self) -> list:
        return [obj.nome for obj in self.objetos]

    @staticmethod
    def aguarda_fala(palavras, limite: int = -1) -> str:
        contador = 0
        palavra_escutada = None
        while palavra_escutada is None:
            palavra_escutada = aguarda_audio(palavras)
            contador += 1
            if limite == contador:
                return None
        return palavra_escutada

    def encontrou_objetos(self) -> bool:
        #if self.mao is None:
        #    return False
        if len(self.objetos) == 0:
            return False
        return True

    def foca_em_objeto(self, objeto: str):
        for o in self.objetos:
            if o.nome == objeto:
                self.objeto_em_mira = o

    def fala_objetos_vistos(self):
        fala = [Audio.EU_VEJO,
                Audio.numero(len(self.objetos)),
                Audio.OBJETOS]
        try:
            self.fala.play(fala)
        except:
            self.fala.beep()
        for objeto in self.objetos:
            print(str(objeto))
            self.fala.falar_objeto(str(objeto))
        print("Encontrei %1d objetos" % len(self.objetos))
        
    def fala_vai_pegar_primeiro(self):
        self.fala.play([Audio.VAMOS_PEGAR])
        self.fala.falar_objeto(str(self.objetos[0]))



