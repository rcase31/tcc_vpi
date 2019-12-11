import cv2
import numpy as np
import time
import google_opencv


def _get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


def desenhar_quadro(frame, x, y, w, h, nome):
    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
    cv2.putText(frame, nome, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)


class ReconhecedorObjetos:
    """

    """

    def mostrar_visao(self):
##        if self.frame is not None:
##            cv2.imshow('img', self.frame)
##            cv2.waitKey(10)
##            # k = cv2.waitKey(30) &
        pass

    def __init__(self):
        # Carrega as redes treinadas do Yolo e do HAAR cascade da mao
        self.Yconfig = 'recursos/yolov3-tiny1.cfg'
        self.Yweights = 'recursos/yolov3-tiny.weights'
        self.Yclasses = 'recursos/yolov3.txt'
        self.cascade = cv2.CascadeClassifier('recursos/palm_v4.xml')
        self.net = cv2.dnn.readNet(self.Yweights, self.Yconfig)
        # Ajusta configuracoes iniciais do OpenCV
        self.cam = None
        self.frame = None
        cv2.startWindowThread()
        # Leitura das classes do Yolo
        self.classes = None
        self.encontrou_mao = False
        with open(self.Yclasses, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

    def __enter__(self):
        # Faz iniciar a captura de video
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            raise IOError("Erro na câmera!")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Libera a camera para demais usos
        self.cam.release()

    def encontrar_mao(self) -> tuple:
        """
        Encontra mao na imagem fornecida pelo Opencv.
        :return: o primeiro quadro de mao encontrado
        """
        ret, self.frame = self.cam.read()
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        hands = self.cascade.detectMultiScale(gray, 1.05, 3)

        for (x, y, w, h) in hands:
            #cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
            #desenhar_quadro(self.frame, x, y, w, h, 'mao')
            # print(x, y, w, h, 'hand')
            self.mostrar_visao()
            self.encontrou_mao = True
            return x, y, w, h, 'hand'
        self.mostrar_visao()
        


        
        return None

    def encontrar_objetos(self) -> list:
        """
        Encontra os objetos usando YOLO
        :return:
        """
        ret, self.frame = self.cam.read()
        largura = self.frame.shape[1]
        altura = self.frame.shape[0]
        scale = 0.00392
        # aqui eu capturo um frame (ou uma foto) do que a camera esta lendo.
        blob = cv2.dnn.blobFromImage(self.frame, scale, (416, 416), (0, 0, 0), True, crop=False)
        # eu jogo minha imagem (ou captura da camera) na rede carregada no opencv
        self.net.setInput(blob)
        # aqui eu testo meu modelo
        outs = self.net.forward(_get_output_layers(self.net))

        # inicializacao
        class_ids = list()
        confidences = list()
        boxes = list()
        conf_threshold = 0.3
        nms_threshold = 0.4

        # Para cada deteccao em cada camada de saida pegar a confianca, id da classe, quadro limitante, e ignore
        # deteccoes fracas (confianca abaixo de 50%)
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.2:
                    center_x = int(detection[0] * largura)
                    center_y = int(detection[1] * altura)
                    w = int(detection[2] * largura)
                    h = int(detection[3] * altura)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
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
            label = self.classes[class_ids[i]]
            #desenhar_quadro(self.frame, x, y, w, h, label)
            saida.append((x, y, w, h, label))
        #self.mostrar_visao()
        return saida

    def loop(self, n_iteracoes: int = None):
        contagem = 0
        tempos = []
        while 1:
            comeco = time.clock()
            self.encontrar_mao()
            self.encontrar_objetos()
            fim = time.clock()
            tempos.append(fim - comeco)
            if n_iteracoes is not None:
                contagem += 1
                if contagem >= n_iteracoes:
                    return tempos

    def atualiza_pos_mao(self, insistencia: int = 5) -> tuple:
        contagem = 0
        coordenadas_mao = None
        while contagem <= insistencia:
            coordenadas_mao = self.encontrar_mao()
            if coordenadas_mao is not None:
                return coordenadas_mao
            contagem += 1
        return coordenadas_mao

    def procurar_c_insistencia(self, insistencia: int = 5, quantidade_maxima: int = 2) -> tuple:
        """
        Permite buscar objetos e maos com o fator de "bouncing" no reconhecimento. Insistencia representa a tolerancia
        a este fator.
        :param insistencia: tolerancia ao fator de bouncing.
        :param quantidade_maxima:
        :return: uma tupla contendo as coordenadas do quadro e os nomes dos objetos, na seguinte estrutura:
        ((x1, y1, x2, y2, mao), (objeto_1, objeto_2,..., objeto_n))
        objeto_n: (x1, y1, x2, y2, nome_do_objeto_ingles)
        """
        contagem = 0
        saida_mao = None
        saida_objetos = ()
        while contagem <= insistencia:
            coordenadas_mao = self.encontrar_mao()
            coordenadas_objetos = self.encontrar_objetos()
            if len(coordenadas_objetos) > len(saida_objetos):
                print('Vi alguma coisa')
                saida_objetos = coordenadas_objetos
            if coordenadas_mao is not None:
                print('Já vejo sua mão')
                saida_mao = coordenadas_mao
            if len(saida_objetos) >= quantidade_maxima and saida_mao is not None:
                return saida_mao, saida_objetos
            contagem += 1

        return saida_mao, saida_objetos


class ReconhecedorObjetosOnline(ReconhecedorObjetos):
    def __init__(self):
        self.cascade = cv2.CascadeClassifier('palm_v4.xml')
        # Ajusta configuracoes iniciais do OpenCV
        self.cam = None
        self.frame = None
        cv2.startWindowThread()
        self.encontrou_mao = False

    def encontrar_objetos(self) -> list:
        """
        Encontro objetos usando a API paga do Google Cloud Vision.
        :return: uma lista de tuplas com a seguinte estrutura (x, y, w, h, nome em ingles).
        """
        # Peco para encontrar a mao primeiro para nao rodar a busca por imagens mais que uma vez, pois o metodo que chama
        # este so retorna quando tanto mao quando objetos forem encontrados na visao da camera.
        print('busca')
        if self.encontrou_mao:
            return google_opencv.localizar_objetos(self.frame)
        else:
            return []
