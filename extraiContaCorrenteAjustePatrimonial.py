import os
import bancoMSC
import json
from datetime import datetime

#Recebe uma lista contendo dicionários com as entradas da MSC, valida contra os domínios buscados e insere os registros
#na respectiva tabela fato

pasta = os.environ.get('PASTA_ORIGEM')

def extraiEntrada(arquivo):
    
    with open(os.path.join(pasta,arquivo), encoding='UTF-8') as datafile:
        balancete = json.loads(datafile.read())    

    contador = {True:0, False:0}
    db = bancoMSC.Conexao()
    
    for i in balancete:
       
        vLnc = int(i["lineNumberCounter"])
        vAmount = float(i["amount"])
        vIdent = int(i["identifier"].split('EX')[0])
        vChave = int(i["chave_sk"])
        vData = i["instant"]
        vMes = int(str(vData)[5:7])
        vAno = int(str(vData)[0:4])
               
        vAccount = i["accountMainID"][:9]
        
        vClasse = int(i["classe"]) # Teste da classe de conta para definir o sql e pesquisar subcontas específicas
        
        dicionarioComum = {":pcasp": vAccount, ":ente": vIdent, ":valor": vAmount, ":coleta": vChave, ":lnc": vLnc, ":meref": vMes, ":anref": vAno}

        if vClasse in [1, 2, 3, 4]:
                
            financeiroPermante = i.get('FP', '')
            if financeiroPermante != '':
                    vFP = int(financeiroPermante[:1])
            else:
                    vFP = ''
            
            dividaConsolidada = i.get('DC', '')
            
            if dividaConsolidada != '':
                    vDC = int(dividaConsolidada[:1])
            else:
                    vDC = ''

            sql = """INSERT INTO TEMP_FATO_PAT(ID_DIM_ENTE, ID_COLETA, ID_DIM_PCASP, ID_ENTRADA_MSC, VA_CONTABIL, ID_DIM_FP, ID_DIM_DC, ME_REFERENCIA, AN_REFERENCIA)
                    VALUES (:ente, :coleta, :pcasp, :lnc, :valor, :fp, :dc, :meref, :anref)"""
            
            dicionarioPatrimonial = {":fp": vFP, ":dc": vDC}
            
            dic_sql = {**dicionarioComum, **dicionarioPatrimonial}

    
            resultado = db.insereAjuste(sql, dic_sql) 
            contador[resultado]+= 1
    
    db.comita()
    os.remove(arquivo)

    print(f"Coleta:{vChave}|Ibge:{vIdent}|Data:{vData}|Sucesso:{contador[True]}|Erros:{contador[False]}")
    
'''    
arquivos = os.listdir(pasta)

for arquivo in arquivos:
    with open(os.path.join(pasta,arquivo), encoding='UTF-8') as datafile:
        balancete = json.loads(datafile.read())
        extraiEntrada(balancete)
    fpath = os.path.join(pasta, arquivo)
    os.remove(fpath)

'''