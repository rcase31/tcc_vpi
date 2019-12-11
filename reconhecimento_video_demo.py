import cv2
import numpy as np
import os.path
import os

import time


def _get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


class ObjetoAvistado():

    traducao = {
        'human': 'humano',
        'hand': 'mão',
        'phone': 'celular',
        'banana': 'banana',
        'apple': 'maçã',
        'fork': 'garfo',
        'bottle': 'garrafa'
    }
    nome = None

    def __init__(self, saida_opencv: tuple):
        nome_ingles = saida_opencv[-1]
        self.nome = self.traducao[nome_ingles]
        self.x_1 = saida_opencv[0]
        self.y_1 = saida_opencv[1]
        self.x_2 = saida_opencv[2] + self.x_1
        self.y_2 = saida_opencv[3] + self.y_1

    # Verifica se um objeto esta mais a direita que outro, ou abaixo
    def __lt__(self, other):
        if other.x_1 > self.x_2 or other.y_1 > self.y_2:
            return True
        else:
            return False

    # Subtracao significa a diferenca, ou seja, distancia de um objeto para o outro
    def __sub__(self, other):
        if self > other:
            return self.epicentro() - other.centro()

    def epicentro(self):
        return (self.x_1 + self.x_2)/2, (self.y_1 + self.y_2)/2


class ReconhecedorObjetos:

    def __init__(self):
        # Carrega as redes treinadas do Yolo e do HAAR cascade da mao
        self.Yconfig = 'recursos\\yolov3-tiny1.cfg'
        self.Yweights = 'recursos\\yolov3-tiny.weights'
        self.Yclasses = 'recursos\\yolov3.txt'
        self.cascade = cv2.CascadeClassifier('recursos\\hand.xml')
        self.net = cv2.dnn.readNet(self.Yweights, self.Yconfig)
        # Ajusta configuracoes iniciais do OpenCV
        self.cam = None
        cv2.startWindowThread()
        # Leitura das classes do Yolo
        self.classes = None
        with open(self.Yclasses, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

    def __enter__(self):
        # Faz iniciar a captura de video
        self.cam = cv2.VideoCapture(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Libera a camera para demais usos
        self.cam.release()

    def encontrar_mao(self) -> tuple:
        """
        Encontra mao na imagem fornecida pelo Opencv.
        :return: o primeiro quadro de mao encontrado
        """
        ret, img = self.cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hands = self.cascade.detectMultiScale(gray, 1.05, 10)

        for (x, y, w, h) in hands:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            # print(x, y, w, h, 'hand')
            return x, y, w, h, 'hand'
        return None

    def encontrar_objetos(self):
        ret, frame = self.cam.read()
        Width = frame.shape[1]
        Height = frame.shape[0]
        scale = 0.00392
        # aqui eu capturo um frame (ou uma foto) do que a camera esta lendo.
        blob = cv2.dnn.blobFromImage(frame, scale, (416, 416), (0, 0, 0), True, crop=False)
        # eu jogo minha imagem (ou captura da camera) na rede carregada no opencv
        self.net.setInput(blob)

        # aqui eu testo meu modelo
        outs = self.net.forward(_get_output_layers(self.net))

        # inicializacao
        class_ids = list()
        confidences = list()
        boxes = list()
        conf_threshold = 0.5
        nms_threshold = 0.4

        # Para cada deteccao em cada camada de saida pegar a confianca, id da classe, quadro limitante, e ignore
        # deteccoes fracas (confianca abaixo de 50%)
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

                # apply non-max suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        # go through the detections remaining
        # after nms and draw bounding box
        saida = []
        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            # print(x, y, w, h, self.classes[class_ids[i]])
            saida.append((x, y, w, h, self.classes[class_ids[i]]))
        return saida

    def loop(self, n_iteracoes: int = None):
        contagem = 0
        tempos = []
        while 1:
            comeco = time.clock()
            print(self.encontrar_mao())
            print(self.encontrar_objetos())
            fim = time.clock()
            tempos.append(fim - comeco)
            if n_iteracoes is not None:
                contagem += 1
                if contagem >= n_iteracoes:
                    return tempos

    def procurar_c_insistencia(self, insistencia: int = 10, quantidade_maxima: int = 3):
        """
        Permite buscar objetos e maos com o fator de "bouncing" no reconhecimento. Insistencia representa a tolerancia
        a este fator.
        :param insistencia: tolerancia ao fator de bouncing.
        :return: TODO: retornar uma tupla contendo instancias de @ObjetoAvistado
        """
        contagem = 0
        saida_mao = None
        saida_objetos = ()
        while contagem <= insistencia:
            coordenadas_mao = self.encontrar_mao()
            coordenadas_objetos = self.encontrar_objetos()
            if len(coordenadas_objetos) >= len(saida_objetos):
                saida_objetos = coordenadas_objetos
            if coordenadas_mao is not None:
                saida_mao = coordenadas_mao
            if len(saida_objetos) > quantidade_maxima and saida_mao is not None:
                return saida_mao, saida_objetos
            contagem += 1
        return saida_mao, saida_objetos



import pandas as pd

o = ReconhecedorObjetos()
with o:
    o.loop()
