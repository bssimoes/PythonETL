import leArquivos
import os
from threading import Thread
import numpy as np
import buscaDimensoes 

#Algoritmo de entrada para o processamento dos arquivos XML da MSC sua carga no banco de dados

pasta = os.environ.get('PASTA_ORIGEM')

if not os.path.isdir(pasta):
    os.mkdir(pasta)

dominioDimensoes = buscaDimensoes.buscaDimensoes() #consulta as tabelas dimensionais e alimenta dois dicionários para validação

arquivosParts = np.array_split(os.listdir(pasta),6) #divide a lista em 6 partes (numPY)

t1 = Thread(target=leArquivos.leArquivo, args=(arquivosParts[0], dominioDimensoes))
t2 = Thread(target=leArquivos.leArquivo, args=(arquivosParts[1], dominioDimensoes))
t3 = Thread(target=leArquivos.leArquivo, args=(arquivosParts[2], dominioDimensoes))
t4 = Thread(target=leArquivos.leArquivo, args=(arquivosParts[3], dominioDimensoes))
t5 = Thread(target=leArquivos.leArquivo, args=(arquivosParts[4], dominioDimensoes))
t6 = Thread(target=leArquivos.leArquivo, args=(arquivosParts[5], dominioDimensoes))
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
