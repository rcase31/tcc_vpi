from reproducao_audio import *
from assistente import Assistente, Estado

if __name__ == '__main__':
    HOT_WORDS = ['Maiara', 'Mayara', 'Nayara']

    mayara = Assistente()
    mayara.estado = Estado.LEITURA

    while True:
        """ Primeiro estado onde a Assistente Virtual (AV) espera ser chamado pela "hot word". Quando acionado, 
        dira "bom dia"
        """
        """ AV faz a leitura dos objetos a sua frente, e diz quais objetos ela viu."
        """
        if mayara.estado == Estado.LEITURA:
            if mayara.procura_objetos():
                mayara.fala_objetos_vistos()
                mayara.fala_vai_pegar_primeiro()
                mayara.avanca_estado()
        """ AV aguarda usuario dizer qual objeto esta procurando.
        """
        if mayara.estado == Estado.AGUARDA_OBJETO:
            mayara.mira_em_primeiro_objeto()
            mayara.estado = Estado.ORIENTACAO
        """ AV vai orientar a mao do usuario a sobrepor o objeto buscado.
        """
        if mayara.estado == Estado.ORIENTACAO:
            with mayara.olhos:
                while not mayara.direciona():
                    pass
            mayara.avanca_estado()
        """ AV diz a mensagem de sucesso quando o objeto eh encontrado
        """
        if mayara.estado == Estado.OBJETO_ENCONTRADO:
            mayara.reproduz_fala(Audio.OBJETO_EM_MIRA)
            mayara.volta_para_estado_inicial()
            mayara.objeto_em_mira = None

