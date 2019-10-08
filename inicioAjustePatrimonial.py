import leArquivos
import os
from threading import Thread
import numpy as np
import ajustePatrimonial, extraiContaCorrenteAjustePatrimonial
import zipfile
import csv
import bancoMSC

#Algoritmo de entrada para o processamento dos arquivos XML da MSC sua carga no banco de dados

pasta = os.environ.get('PASTA_ORIGEM')
pastazip = os.environ.get('PASTA_ZIP')

db = bancoMSC.Conexao()
listaAnterior = db.buscaDimensao('select distinct id_coleta from temp_fato_pat')
db.desconectaBanco()

#Descompacta arquivos
listaZip = os.listdir(pastazip)

for izip in listaZip:
    nome = izip.split(".")[0]
    idColeta = int(nome.split("_")[0])
    if idColeta not in listaAnterior:
        with zipfile.ZipFile(os.path.join(pastazip, izip), 'r') as zip_ref:
            zip_ref.extractall(pasta)
        old_file = os.path.join(pasta, "instancia.xml")
        new_file = os.path.join(pasta, f'{nome}.xml')
        os.rename(old_file, new_file)
        ajustePatrimonial.leArquivo(new_file)
    else:
        print(f'Coleta {idColeta} já inserida!')
'''
listaExecutada = os.listdir(pasta)
with open('C:\\leitura\\leitura.csv', 'w', newline='') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(listaExecutada)

if not os.path.isdir(pasta):
    os.mkdir(pasta)

arquivos = os.listdir(pasta)


'''

