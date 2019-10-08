# -*- coding: utf-8 -*-
import cx_Oracle
import os

ip = '10.229.41.27'
port = 1521
service_name = 'bd3prd'
dsn = cx_Oracle.makedsn(ip, port, service_name)
db =  cx_Oracle.connect( os.environ.get('ORACLE_USER_STG'), os.environ.get('ORACLE_PASSWORD_STG'), dsn)

cursor = db.cursor()
cursorMview = db.cursor()
cursor.execute('ALTER SESSION FORCE PARALLEL DML')

try:
    # Testando o DBLINK
    cursor.execute('select * from dual@DL_STG_SICONFI')
except Exception as e:
    print(e)
    exit(1)

try:
    # truncando e ajustando a tabela para nao gerar log
    
    cursor.execute('truncate table COLETA drop storage')
    cursor.execute('ALTER TABLE COLETA NOLOGGING')

    sql = """
        INSERT /*+ PARALLEL(COLETA,5) */ INTO COLETA 
        SELECT /*+ PARALLEL(COLETA,5) */ * FROM SICONFI.COLETA@dl_stg_siconfi
    """
    cursor.execute(sql)
    db.commit()
    print('Tabela COLETA atualizada')

    cursor.execute('ALTER TABLE XBRL_FATONUMERICO  NOLOGGING')
    cursor.execute('truncate table XBRL_FATONUMERICO')
    sql = """
        INSERT /*+ PARALLEL(XBRL_FATONUMERICO,5) */ INTO XBRL_FATONUMERICO 
        SELECT /*+ PARALLEL(XBRL_FATONUMERICO,5) */ * FROM SICONFI.XBRL_FATONUMERICO@dl_stg_siconfi
    """
    cursor.execute(sql)
    db.commit()
    print('Tabela XBRL_FATONUMERICO atualizada')

    cursor.execute('truncate table COLETA_MATRIZ drop storage')
    cursor.execute('ALTER TABLE COLETA_MATRIZ  NOLOGGING')
    
    sql = """
        INSERT /*+ PARALLEL(XBRL_FATONUMERICO,5) */ INTO COLETA_MATRIZ 
        SELECT /*+ PARALLEL(XBRL_FATONUMERICO,5) */ * FROM SICONFI.COLETA_MATRIZ@dl_stg_siconfi  
    """
    cursor.execute(sql)
    db.commit()
    print('Tabela COLETA_MATRIZ atualizada')

    cursor.execute('truncate table INSTANCIA_COLETA_MATRIZ drop storage')
    sql = """
        INSERT /*+ PARALLEL(XBRL_FATONUMERICO,5) */ INTO INSTANCIA_COLETA_MATRIZ 
        SELECT /*+ PARALLEL(XBRL_FATONUMERICO,5) */ * FROM SICONFI.INSTANCIA_COLETA_MATRIZ@dl_stg_siconfi 
    """
    cursor.execute(sql)
    db.commit()
    print('Tabela INSTANCIA_COLETA_MATRIZ atualizada')


except Exception as e:
    print(e)
    exit(1)


print( 'Stage Atualizado!' )



    
