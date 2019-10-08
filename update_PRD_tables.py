# -*- coding: utf-8 -*-
import cx_Oracle
import os
import datetime

ip = '10.229.41.27'
port = 1521
service_name = 'bd3prd'
dsn = cx_Oracle.makedsn(ip, port, service_name)
db =  cx_Oracle.connect( os.environ.get('ORACLE_USER'), os.environ.get('ORACLE_PASSWORD'), dsn)

cursor = db.cursor()
cursorMview = db.cursor()

print(f'Conectado como {os.environ.get("ORACLE_USER")}')
print (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))

try:
    # Testando o STG
    cursor.execute('select count(*) from STG_SICONFI.xbrl_fatonumerico')
    count = cursor.fetchone()
    if count[0] < 1: 
        raise Exception('State não está atualizado')
    
    
except Exception as e:
    print(e)
    exit(1)

try:
    # truncando e ajustando a tabela para nao gerar log
    cursor.execute('truncate table XBRL_FATONUMERICO DROP STORAGE')
    cursor.execute('ALTER TABLE XBRL_FATONUMERICO NOLOGGING')

    cursor.execute('ALTER SESSION FORCE PARALLEL DML')

    sql = """
       INSERT /*+ PARALLEL(4) */ INTO XBRL_FATONUMERICO 
        SELECT /*+ PARALLEL(4) */ 
        a.id_coleta_sk, a.XBRL_FATONUMERICO_SK,
        a.an_exercicio,a.co_tipo_demonstrativo,a.no_anexo,
        a.nr_periodo,a.in_periodicidade,a.CO_ESFERA,a.co_poder,a.co_regiao, a.sg_ente ,a.ELEMENTNAME,  a.elementlabel, 
        a.no_label_eixo_x ,  a.no_label_eixo_y , a.value, 
        a.enddate, a.startdate, a.nr_pos_anexo, a.nr_pos_tabela, 
        c.no_orgao, c.id_ente,
        d.NR_IBGE_RED,d.no_ente, ex.qt_habitante ,a.NO_LABEL_ROTULO,  a.id_eixo_x
        from stg_siconfi.xbrl_fatonumerico a 
        join stg_siconfi.coleta b on a.id_coleta_sk = b.id_coleta_sk
        join stg_siconfi.orgao c on b.id_orgao_sk = c.id_orgao_sk
        join stg_siconfi.ente d on c.id_ente = d.id_ente
        left join stg_siconfi.excepcionalidade_habitante ex on (d.id_ente = ex.id_ente and ex.an_exercicio = a.an_exercicio)
        left join stg_siconfi.historico_hab_estatistica he on (a.id_coleta_sk = he.id_coleta_sk)
        where he.sn_participa_estatistica = 1 or he.sn_participa_estatistica is null
    """
    cursor.execute(sql)
    db.commit()
    print('Tabela XBRL_FATONUMERICO atualizada')


    cmdInMemory = """
    begin
        DBMS_INMEMORY.POPULATE('DEV_SICONFI','XBRL_FATONUMERICO');
    end;
    """
    cursorMview.execute(cmdInMemory)

    # forçar o dado ir para memória
    cursor.execute('select * from XBRL_FATONUMERICO')
   


except Exception as e:
    print(e)
    print (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    exit(1)

print( 'Stage Atualizado!' )
print (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))



    
