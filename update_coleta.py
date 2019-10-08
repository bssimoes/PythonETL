import cx_Oracle
import os

def connectOracle():
    ip = '10.229.41.27'
    port = 1521
    service_name = 'bd3prd'
    dsn = cx_Oracle.makedsn(ip, port, service_name)
    return  cx_Oracle.connect( os.environ.get('ORACLE_USER_STG'), os.environ.get('ORACLE_PASSWORD_STG'), dsn)


db = connectOracle()
print("Conectado ao Oracle com o usuario "+ os.environ.get('ORACLE_USER'))
cursor = db.cursor()


try:
    
    #o que tem aqui e não tem la (precisa alterar sn_antigo = 'S') - XBRL_FATONUMERICO
    sqlUpdateXbrlFatoNumerico = """
    update stg_siconfi.xbrl_fatonumerico set sn_antigo = 'S' where id_coleta_sk in (
        select id_coleta_sk from (
            select id_coleta_sk, dt_status_coleta from stg_siconfi.coleta where (sn_antigo <> 'S' or sn_antigo is null)
        minus 
            select  id_coleta_sk, dt_status_coleta from siconfi.coleta@dl_stg_siconfi
        )
    )
    """ 
    print('==============================================')
    print('Localizando e alterando fatos numericos(XBRL_FATONUMERICO) antigos...')
    cursor.execute(sqlUpdateXbrlFatoNumerico)
    print( 'Fatos Alterados: ' + str(cursor.rowcount) )
   

    #o que tem la e não tem aqui (precisa inserir) - XBRL_FATONUMERICO
    sqlInsertXbrlFatoNumerico = """
    insert into stg_siconfi.xbrl_fatonumerico 
       select col.*,'' sn_antigo from siconfi.xbrl_fatonumerico@dl_stg_siconfi col where id_coleta_sk in(
            select id_coleta_sk from (
                select  id_coleta_sk, dt_status_coleta  from siconfi.coleta@dl_stg_siconfi 
                minus 
                select id_coleta_sk, dt_status_coleta from stg_siconfi.coleta where (sn_antigo <> 'S' or sn_antigo is null) 
            )
        )
    """
    print('==============================================')     
    print('Inserindo novos dados em XBRL_FATONUMERICO...')
    cursor.execute(sqlInsertXbrlFatoNumerico)
    print( 'Fatos Numericos Inseridos: ' + str(cursor.rowcount) )


    #o que tem aqui e não tem la (precisa alterar sn_antigo = 'S')
    sqlUpdateXbrlFatoNumerico = """
    update stg_siconfi.coleta set sn_antigo = 'S' where id_coleta_sk in (
        select id_coleta_sk from (
            select id_coleta_sk, dt_status_coleta from stg_siconfi.coleta where (sn_antigo <> 'S'  or sn_antigo is null)
            minus 
            select  id_coleta_sk, dt_status_coleta from siconfi.coleta@dl_stg_siconfi
        )
    )
    """
    print('==============================================')
    print('Localizando e alterando coletas antigas...')
    cursor.execute(sqlUpdateXbrlFatoNumerico)
    print( 'Coletas Alteradas: ' + str(cursor.rowcount) )

    
    
    #o que tem la e não tem aqui (precisa inserir) - COLETA
    sqlInsertColeta = """
    insert into stg_siconfi.coleta 
        select col.*,'' sn_antigo from siconfi.coleta@dl_stg_siconfi col where id_coleta_sk in(
            select id_coleta_sk from (
                select  id_coleta_sk, dt_status_coleta from siconfi.coleta@dl_stg_siconfi
                minus 
                select id_coleta_sk, dt_status_coleta from stg_siconfi.coleta where (sn_antigo <> 'S'  or sn_antigo is null)
            )
        )
    """
    print('==============================================')
    print('Inserindo novas coletas...')
    cursor.execute(sqlInsertColeta)
    print( 'Coletas Inseridas: ' + str(cursor.rowcount) )

    

    db.commit();
    print ('COMMIT EFETUADO!')
except Exception as e:
    print("Erro ="+str(e))
    print ('ROWBACK EFETUADO!')

print ('SICONFI DW ATUALIZADO COM SUCESSO!')

    