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
   
    # atualizando todas as mviews
    cursor.execute('select mview_name from user_mviews order by mview_name')
    for mview in cursor:
        cmd = f"""
            begin
            DBMS_SNAPSHOT.REFRESH( '{mview[0]}' , 'C', ATOMIC_REFRESH => FALSE);
            end;
            """
        print(f'Mview {mview[0]} atualizando...!')
        cursorMview.execute(cmd)
        print(f'Mview {mview[0]} atualizando!')


except Exception as e:
    print(e)
    print (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    exit(1)

print( 'Stage Atualizado!' )
print (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))



    
