# -*- coding: utf-8 -*-
import cx_Oracle
import zipfile
import os

def connectOracle():
    ip = '10.229.41.27'
    port = 1521
    service_name = 'bd3prd'
    dsn = cx_Oracle.makedsn(ip, port, service_name)
    return  cx_Oracle.connect( os.environ.get('ORACLE_USER'), os.environ.get('ORACLE_PASSWORD'), dsn)

db = connectOracle()
print("Conectado ao Oracle com o usuario "+ os.environ.get('ORACLE_USER'))
cursor = db.cursor()

pastaOrigem = os.environ.get('PASTA_ORIGEM')
pastaZip = os.environ.get('PASTA_ZIP')

if not os.path.isdir(pastaOrigem):
    os.mkdir(pastaOrigem)

if not os.path.isdir(pastaZip):
    os.mkdir(pastaZip)

sqlGetNewColects = """ 
 with max_date as (
(SELECT NVL(MAX(DT_ATUALIZACAO), TO_DATE('2019/01/01', 'yyyy/mm/dd') ) AS dt_atualizacao FROM VW_FATO_MSC) 
)
 select CM.ID_COLETA_MATRIZ_SK, ma.co_tipo_matriz, I.aq_instancia_xmlzip from STG_SICONFI.INSTANCIA_COLETA_MATRIZ I
 JOIN STG_SICONFI.COLETA_MATRIZ CM ON i.id_instancia_coleta_matriz_sk = cm.id_instancia_coleta_matriz_sk
 JOIN STG_SICONFI.TAXONOMIA_MATRIZ TM ON CM.ID_TAXONOMIA_MATRIZ_SK = tm.id_taxonomia_matriz_sk
 JOIN STG_SICONFI.MATRIZ MA ON TM.ID_MATRIZ_SK = MA.ID_MATRIZ_SK
 JOIN max_date m on (CM.DT_ATUALIZACAO > m.dt_atualizacao)
 JOIN STG_SICONFI.orgao org on (org.id_orgao_sk = cm.id_orgao_sk) and (org.co_poder = 'E')
 WHERE MA.AN_EXERCICIO >= 2019

"""

cursor.execute(sqlGetNewColects) 
for result in cursor:
    
    chave_coleta_sk = result[0]
    co_tipo_matriz = result[1]
    zipBlob = result[-1]

    # salvando as instancias no formato zip
    zipfileName  = os.path.join(pastaZip,str(chave_coleta_sk)+'_'+str(co_tipo_matriz)+'.zip')
    zipFile = open(zipfileName,'wb')
    zipFile.write(zipBlob.read())
    zipFile.close()

    # descompactando as instancias
    zip_ref = zipfile.ZipFile(zipfileName, 'r')
    zip_ref.extractall(pastaOrigem)
    zip_ref.close()

    # renomeando para o nome do arquivo ficar como ID
    old_file = os.path.join(pastaOrigem, "instancia.xml")
    new_file = os.path.join(pastaOrigem, str(chave_coleta_sk)+'_'+str(co_tipo_matriz)+'.xml')
    os.rename(old_file, new_file)

    print('Arquivo copiado: '+new_file )
    
cursor.close()
db.close()

print('Fim dos Arquivos')