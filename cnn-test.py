"""
Fonte:
https://towardsdatascience.com/building-a-convolutional-neural-network-cnn-in-keras-329fbbadc5f5
"""
"""
Bloco 1 - importação de bibliotecas 
"""
from keras.datasets import mnist
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten


"""
Bloco 2 - download das imagens de calibração do modelo

Carregamento da base de dados da biblioteca Keras. Em mnist são 60.000 imagens para treinamento, e 10.000, para teste;
sendo assim 70.000 imagens na totalidade.
X_train e X_test representam vetores de matrizes com o desenho de números, detalhando em escala de cinza cada pixel das 
imagens.
y_train e y_test representam vetores com os valores corretos correspondentes às matrizes de X.
Assim, X têm 3 dimensões, enquanto y têm apenas 1.
"""
(X_train, y_train), (X_test, y_test) = mnist.load_data()
# Correção da escala dos valores. Valor máximo deve ser 1, e não 255.
X_train, X_test = X_train / 255.0, X_test / 255.0
# Impressão gráfica de um dos elementos da entrada
plt.imshow(X_train[0])


"""
Bloco 3 - redimensionamento das matrizes de entrada

As linhas de código abaixo mudam o arranjo das matrizes contendo as imagens. Isso é necessário por conta do formato ao 
qual o modelo espera como entrada. Caso o conjunto de imagens fosse colorido, o último parâmetro do método reshape() 
seria diferente de 1. Quanto aos outros parâmetros deste método, tem-se:
    -Primeiro parâmetro é a quantidade de imagens;
    -Segundo parâmetro é a dimensão das imagens.
Vale ressaltar que não houve mudança na quantidade de imagens aqui, nem perda de resolução.
"""
X_train = X_train.reshape(60000,28,28,1)
X_test = X_test.reshape(10000,28,28,1)


"""
Bloco 4 - conversão dos vetores de resposta para variáveis binárias

Torna as variáveis-resposta em vetores binários. Este passo é essencial para adequação ao modelo, que prevê uma saída 
binária, ainda que com múltiplos nós de saída. O autor usa o termo "one-hot encode target column", que significa 
basicamente as saídas binárias.
"""
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)
y_train[0]

"""
Bloco 5 - desenho do modelo de CNN

Modelo usado aqui é o sequencial. Permite construir o modelo camada a camada.
Sendo assim, o método add() nos permite adicionar tais camadas ao modelo.
Kernel size significa o tamanho da matriz de convolução.

Segmento de código para construir e configurar o modelo a ser usado. Utiliza-se uma instância do modelo sequencial.
A característica deste modelo é a adição sequencial de camadas.
As camadas aqui adicionadas são recomendações do autor do artigo. Vale ressaltar que existe extenso estudo a respeito
do número de nós e outros parâmetros aqui utilizados, mas entende-se que sairia do escopo do projeto estudar quais 
seriam valores ótimos para cada caso, então segue-se com a recomendação do autor. Quanto aos outros parâmetros de 
entrada, bem como as camadas utilizadas, vale listar cada aspecto.
    -Método add() da classe Sequential() é aquele que permite a adição das camadas.
    -Parâmetro de entrada kernel_size significa o tamanho da matriz de convolução, em outras palavras, é o tamanho do 
    filtro que percorrerá cada pixel da imagem.
    -Parâmetro de entrada activation significa a curva de da função de ativação; neste caso utilizou-se a ReLU, cuja 
    função matemática é R(z) = max(0, z), e é a mais utilizada para CNN. Para a última camada, foi utilizada a curva 
    de ativação softmax, cuja forma é uma transição suave entre 0 e 1, podendo traduzir na probabilidade de dedução do 
    modelo, que deve variar entre 0e 100%.
    -Note que input_shape representa as dimensões de cada imagem nas matrizes de entrada, após o uso da função 
    reshape().
    -Conv2D() são camadas de matrizes bidimencionais de convolução.
    -Flatten() representa uma camada de adequação entre as camadas Conv2D e Dense; em inglês significa achatamento.
    -Dense() é uma camada unidimensional frequentemente usada em redes neurais; neste caso oferece 10 saídas possíveis,
    cada qual com uma probabilidade associada. Idealmente apenas uma das saídas deve apresentar valor de probabilidade
    elevado.
"""
# Criando uma instância de modelo sequencial (permite adição sequencial de camadas).
model = Sequential()
# Adicionando as camadas
model.add(Conv2D(filters=64, kernel_size=3, activation='relu', input_shape=(28,28,1)))
model.add(Conv2D(filters=32, kernel_size=3, activation='relu'))
model.add(Flatten())
model.add(Dense(units=10, activation='softmax'))
#TODO: verificar se é possivel salvar o modelo para depois ser importado

#TODO: terminar descrição
"""
Bloco 6 - carregamento do modelo e junção das camadas

Trecho abaixo faz a junção das camadas do modelo. Perceba que a natureza do modelo prevê primeiro a adição de camadas,
seguida pela junção através de método da classe respectiva. Os parâmetros aqui utilizados são:
    -optimizer: parâmetro responsável pelo controle no ritmo de aprendizado. O autor recomenda o 'adam' e diz que há um
    trade-off entre agilidade e acurácia.
    -loss:
    -metrics: aqui usa-se a acurácia para medir performance e calibrar o modelo. (FALAR SOBRE QUAIS SERIAM AS OUTRAS OPÇÕES
""" 
#compile model using accuracy to measure model performance
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

"""
Bloco 7 - treino

Finalmente se faz o treinamento do modelo. Aqui se utiliza a entrada e a saída providas pela biblioteca mnist do keras.
Também se coloca os conjuntos de teste. "epochs" representa o número de iterações para o modelo, cuja recomendação do 
autor aqui é 3; o aumento deste valor costuma melhorar o poder preditivo do modelo, mas também com maior tempo de pro-
cessamento, até determinado ponto, onde pode ocorrer "overfitting".
"""
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=3)

"""
Bloco 8 - predição

A partir daqui o modelo já está treinado e pronto para uso.
Fazendo predições para as 4 primeiras imagens no conjunto de imagens separadas para teste. O método abaixo devolve um 
vetor de predição.
"""
model.predict(X_test[:4])

"""
Bloco 9 - averiguação

Averiguando o conjunto de 4 imagens.
"""
y_test[:4]
