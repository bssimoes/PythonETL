import os
import xml.etree.cElementTree as ET
import bancoMSC
import extraiDados
from datetime import datetime
import buscaDimensoes
import re

#Função que lê um arquivo XML da Matriz de Saldos Contábeis e converte para uma lista contendo dicionários de chave-valor

fatos = ['{http://www.xbrl.org/int/gl/cor/2015-03-25}lineNumberCounter',
         '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountMainID',
         '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountMainDescription',
         '{http://www.xbrl.org/int/gl/cor/2015-03-25}amount', '{http://www.xbrl.org/int/gl/cor/2015-03-25}signOfAmount',
         '{http://www.xbrl.org/int/gl/cor/2015-03-25}debitCreditCode',
         '{http://www.xbrl.org/int/gl/cor/2015-03-25}xbrlInclude']
subcontas = ['{http://www.xbrl.org/int/gl/cor/2015-03-25}accountSubID',
             '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountSubType']
entryDetail = '{http://www.xbrl.org/int/gl/cor/2015-03-25}entryDetail'
accountSub = '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountSub'

chaves = ['chave_sk','lineNumberCounter','classe', 'accountMainID', 'accountMainDescription', 'amount', 'signOfAmount', 'debitCreditCode', 'xbrlInclude', 'identifier', 'instant', 'atualizacao']

pasta = os.environ.get('PASTA_ORIGEM')

def leArquivo(arquivos, dominio):
    db = bancoMSC.Conexao()

    for arquivo in arquivos:
        registros_desprezados = 0
        balancete = []

        fullname = os.path.join(pasta, arquivo)
        lista_nome = os.path.splitext(arquivo)[0].split("_")
        tab_nome = lista_nome[0]
        tipo_msc = lista_nome[1]
        #apaga os registros desatualizados das tabelas fato
        apagaFatoPatrimonial = f'DELETE FROM FATO_MSC_PATRIMONIAL WHERE ID_COLETA = {int(tab_nome)}'
        db.limpaRegistros(apagaFatoPatrimonial, tab_nome)

        apagaFatoControle = f'DELETE FROM FATO_MSC_CONTROLE WHERE ID_COLETA = {int(tab_nome)}'
        db.limpaRegistros(apagaFatoControle, tab_nome)
        
        apagaFatoOrcamentaria = f'DELETE FROM FATO_MSC_ORCAMENTARIA WHERE ID_COLETA = {int(tab_nome)}'
        db.limpaRegistros(apagaFatoOrcamentaria, tab_nome)

        contx = {}
        contx['chave_sk'] = tab_nome
        contx['tipo_msc'] = tipo_msc
        list_resultados = db.buscaAtualizacao(tab_nome)
        contx['atualizacao'] = list_resultados[0][1]
                
        num_reg = 0

        xml_iter = ET.iterparse(fullname, events=('start', 'end'))

        for event, elem in xml_iter:
            
            elemento = str(elem.tag).split("}", 1)[1]
            dicionario = [elemento, elem.text]

            if event == 'end' and elem.tag == '{http://www.xbrl.org/2003/instance}identifier': # verifica a tag identifier
                contx[str(dicionario[0])] = dicionario[1]
            elif event == 'end' and elem.tag == '{http://www.xbrl.org/2003/instance}instant': # verifica a tag instant
                try:
                    contx[str(dicionario[0])] = datetime.strptime(dicionario[1],"%Y-%m-%d")
                except Exception as e:
                    print(f"Erro no arquivo={arquivo}, data em formato incorreto, erro={str(e)}")
                    break
            elif event == 'start' and elem.tag == entryDetail:  # verifica se um entryDetail foi aberto
                fatx = {}
            elif event == 'end' and elem.tag in fatos:  # verifica se o elemento listado está no array de fatos desejados
                if elemento == 'accountMainID':
                    fatx[str(dicionario[0])] = dicionario[1] if dicionario[1] is not None and elem.text.isdigit() else ''
                elif elemento == 'amount':
                    fatx[str(dicionario[0])] = dicionario[1] if dicionario[1] is not None else ''
                else:
                    fatx[str(dicionario[0])] = dicionario[1] if dicionario[1] is not None else ''
            elif event == 'start' and elem.tag == accountSub:  # verifica se está passando uma subconta
                subdic = {}
            elif event == 'end' and elem.tag in subcontas:  # verifica se está fechando uma conta corrente
                if elemento == 'accountSubType':
                    chave = elem.text if elem.text is not None else ''
                elif elemento == 'accountSubID':
                    if elem.text is None:
                        valor = ''
                    elif not elem.text.isdigit():
                        valor = ''
                    elif elem.text == '0':
                        valor = ''
                    else:
                        valor = elem.text
            elif event == 'end' and elem.tag == accountSub:
                subdic[str(chave)] = valor
                fatx.update(subdic)
            elif event == 'end' and elem.tag == entryDetail:  # verifica se o entryDetail foi fechado
                try:
                    fatx['classe'] = int(fatx['accountMainID'][0])
                    fatx['amount'] = float(fatx['amount'])
                    fatx.update(contx)
                    elem.clear()
                    balancete.append(fatx)
                    num_reg += 1
                except Exception as e:
                    registros_desprezados += 1
                    elem.clear()
                    continue

        if len(balancete) == 0:
            print(f"Coleta{tab_nome}|TipoM:{tipo_msc}|Ibge:{contx['identifier'].split('EX')[0]}|Data:{contx['instant']}|Sucesso:|Erros:|Deprezados:")
            os.remove(fullname)
        else:
            extraiDados.extraiEntrada(balancete, num_reg, arquivo, db, dominio, registros_desprezados)

    db.desconectaBanco()