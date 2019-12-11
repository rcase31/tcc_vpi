from pygame import mixer  # Load the popular external library
from enum import Enum
import time
import glob


# fonte: https://soundoftext.com/
class Audio(Enum):
    _caminho_falas = 'falas/'
    BOM_DIA = _caminho_falas + 'bom dia.mp3'
    OBJETO_ENCONTRADO = _caminho_falas + 'objeto encontrado.mp3'
    QUAL_DESEJA = _caminho_falas + 'qual deles voce deseja.mp3'
    EU_VEJO = _caminho_falas + 'eu vejo.mp3'
    OBJETOS = _caminho_falas + 'objetos.mp3'
    TRES = _caminho_falas + '3.mp3'
    DOIS = _caminho_falas + '2.mp3'
    UM = _caminho_falas + '1.mp3'
    SMALL_BEEP = _caminho_falas + 'beep.mp3'
    OBJETO_DESCONHECIDO = _caminho_falas + 'um objeto desconhecido.mp3'
    DIREITA = _caminho_falas + 'direita.mp3'
    ESQUERDA = _caminho_falas + 'esquerda.mp3'
    ACIMA = _caminho_falas + 'acima.mp3'
    ABAIXO = _caminho_falas + 'abaixo.mp3'
    OBJETO_EM_MIRA = _caminho_falas + 'objeto buscado em mira.mp3'
    NAO_ENTENDI = _caminho_falas + 'nao entendi.mp3'
    NAO_VEJO_MAO = _caminho_falas + 'nao vejo mais sua mao.mp3'
    VAMOS_PEGAR = _caminho_falas + 'vamos pegar.mp3'

    @property
    def caminho_falas(self):
        return self._caminho_falas

    def __str__(self):
        return self.value

    @staticmethod
    def numero(num: int):
        if num == 1:
            return Audio.UM
        if num == 2:
            return Audio.DOIS
        if num > 2:
            return Audio.TRES


class PlayerAudio:

    def __enter__(self):
        mixer.init()

    def __exit__(self, exc_type, exc_val, exc_tb):
        mixer.stop()

    def play(self, caminho: Audio = None):
        with self:
            if not isinstance(caminho, list):
                caminho = [caminho]
            for c in caminho:
                print('str(c)')
                mixer.music.load(str(c))
                mixer.music.play()
                time.sleep(len(str(c)) / 7)

    def beep(self):
        with self:
            self.play(Audio.SMALL_BEEP)

    def falar_objeto(self, objeto: str):
        arquivos = glob.glob('falas/*' + objeto + '*')
        if len(arquivos) == 0:
            fala = Audio.OBJETO_DESCONHECIDO
        else:
            fala = arquivos[0]
        with self:
            self.play(fala)
p = PlayerAudio()
p.beep()