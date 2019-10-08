import cx_Oracle
import os

ip = '10.229.41.27'
port = 1521
service_name = 'bd3prd'
dsn = cx_Oracle.makedsn(ip, port, service_name)
db =  cx_Oracle.connect( os.environ.get('ORACLE_USER_STG'), os.environ.get('ORACLE_PASSWORD_STG'), dsn)

cursor = db.cursor()
cursorMview = db.cursor()
print(f'Conectado como {os.environ.get("ORACLE_USER_STG")}')

cursor.execute('ALTER SESSION FORCE PARALLEL DML')

try:
    # Testando o DBLINK
    cursor.execute('select * from dual@DL_STG_SICONFI')
except Exception as e:
    print(e)
    exit(1)

# atualizando todas as mviews
cursor.execute('select mview_name from user_mviews order by mview_name')
for mview in cursor:
    cmd = f"""
        begin
        DBMS_SNAPSHOT.REFRESH( '{mview[0]}' , 'C', ATOMIC_REFRESH => FALSE);
        end;
        """
    try:    
        cursorMview.execute(cmd)
        print(f'Mview {mview[0]} atualizado!')

    except Exception as e:
            print(e)
            print(f'Mview {mview[0]} falhou!')

