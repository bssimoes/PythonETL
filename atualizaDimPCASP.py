import bancoMSC
import pandas as pd
import os

df = pd.read_csv('C:\\Projetos_Python\\dw-siconfi\\fontes\\dimensoes\\DIM_PCASP_ESTENDIDO.csv', encoding='utf-8')

db = bancoMSC.conectaBanco()

for index, row in df.iterrows():
    conta = str(row['ID_DIM_PCASP'])
    titulo = row['NO_TITULO']
    ano = int(row['AN_REFERENCIA'])

    query = "INSERT INTO DIM_PCASP_ESTENDIDO(ID_DIM_PCASP, NO_TITULO, AN_REFERENCIA) VALUES( :conta, :titulo, :ano )"
    
    relacao = {':conta': conta, ':titulo': titulo, ':ano': ano}

    bancoMSC.insereDimPcasp(db, query, relacao)

db.commit()
bancoMSC.desconectaBanco(db)