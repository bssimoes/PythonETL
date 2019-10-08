import cx_Oracle
import os

class Conexao():
    def __init__(self):
        ip = '10.229.41.27'
        port = 1521
        SID = 'bd3prd'
        dsn_tns = cx_Oracle.makedsn(ip, port, SID)
        self.conexao = cx_Oracle.connect(os.environ.get('ORACLE_USER'), os.environ.get('ORACLE_PASSWORD'), dsn_tns)

    def desconectaBanco(self):
        self.conexao.close()

    def proxSequencia(self, sequencia):
        cursor = self.conexao.cursor()
        cursor.execute(f'select {sequencia}.nextval from dual')
        seq = int(cursor.fetchone()[0])
        cursor.close()
        return seq

    def buscaAtualizacao(self, id):
        sql = f'select id_coleta_matriz_sk, dt_atualizacao from STG_SICONFI.coleta_matriz where id_coleta_matriz_sk = {id}'
        cursor = self.conexao.cursor()
        cursor.execute(sql)
        resultados = []
        for row in cursor.fetchall():
            resultados.append(row)
        return resultados

    def insereDados(self, sql, dicionario, arquivo, ide, linha):    
        cursor_insert = self.conexao.cursor()
        id_col = int(arquivo.split("_")[0])
        is_sucesso = True
        try:
            cursor_insert.execute(sql, dicionario)
        except Exception as e:
            #print(f"Erro no arquivo={arquivo}, entrada={linha}, erro={str(e)}")
            query = """INSERT INTO LOG_FATO_MSC(ID_LOG, ID_ENTRADA_MSC, NO_ERRO, ID_COLETA)    
                    VALUES( :ID, :ENT, :ERR, :COL )"""
            qdict = {':ID': ide, ':ENT': linha, ':ERR': str(e), ':COL':id_col}
            cursor_insert.execute(query, qdict)
            is_sucesso = False
        cursor_insert.close()
        return is_sucesso

    def insereSubConta(self, sql, dicionario, arquivo):
        cursor_insert = self.conexao.cursor()
        try:
            cursor_insert.execute(sql, dicionario)
        except:
            dicionario[':tipo'] = ''
            dicionario[':id'] = ''
            dicionario[':err'] = 'S'
            cursor_insert.execute(sql, dicionario)

        cursor_insert.close()
        self.conexao.commit()

    def limpaRegistros(self, sql, arquivo):
        cursor_delete = self.conexao.cursor()
        try:
            cursor_delete.execute(sql)
        except Exception as e:
            print(f"Erro ao deletar o registro do arquivo: {arquivo}, erro={str(e)}")
        cursor_delete.close()


    def insereDimPcasp(self, sql, dicionario):
        cursor_insert = self.conexao.cursor()
        try:
            cursor_insert.execute(sql, dicionario)
        except Exception as e:
            print(f"Erro ao inserir conta do comando: {sql}, erro={str(e)}")

        cursor_insert.close()

    def buscaDimensao(self, sql):
        cursor = self.conexao.cursor()
        cursor.execute(sql)
        resultados = [row[0] for row in cursor.fetchall()]
        return resultados
    
    def comita(self):
        self.conexao.commit()

    def insereAjuste(self, sql, dicionario):    
        cursor_insert = self.conexao.cursor()
        is_sucesso = True
        try:
            cursor_insert.execute(sql, dicionario)
        except Exception as e:
            print(f"Erro={str(e)}")
            is_sucesso = False
        cursor_insert.close()
        return is_sucesso