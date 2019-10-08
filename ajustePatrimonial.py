import os
import xml.etree.cElementTree as ET
import bancoMSC
import extraiDados
from datetime import datetime
import buscaDimensoes
import re
import json
import extraiContaCorrenteAjustePatrimonial

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


def leArquivo(arquivo):
    
    #for arquivo in arquivos:
    registros_desprezados = 0
    balancete = []

    #fullname = os.path.join(pasta, arquivo)
    lista_nome = os.path.split(arquivo)
    tab_nome = lista_nome[-1].split("_")[0]
    #tipo_msc = lista_nome[1]

    contx = {}
    contx['chave_sk'] = tab_nome
    #contx['tipo_msc'] = tipo_msc
            
    num_reg = 0

    xml_iter = ET.iterparse(arquivo, events=('start', 'end'))

    for event, elem in xml_iter:
        
        elemento = str(elem.tag).split("}", 1)[1]
        dicionario = [elemento, elem.text]

        if event == 'end' and elem.tag == '{http://www.xbrl.org/2003/instance}identifier': # verifica a tag identifier
            contx[str(dicionario[0])] = dicionario[1]
        elif event == 'end' and elem.tag == '{http://www.xbrl.org/2003/instance}instant': # verifica a tag instant
            try:
                contx[str(dicionario[0])] = dicionario[1]
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
                if fatx['classe'] < 5:
                    balancete.append(fatx)
                    num_reg += 1
                else:
                    registros_desprezados += 1    
            except Exception as e:
                registros_desprezados += 1
                elem.clear()
                continue

    if len(balancete) == 0:
        print(f"Arquivo vazio")
        os.remove(os.path.join(pasta,arquivo))
    else:
        arquivoSaida = os.path.join(pasta,f'{tab_nome}.json')
        with open(arquivoSaida, 'w', encoding='UTF-8') as ef:
            json.dump(balancete, ef)
            print(f'{arquivoSaida} salvo com sucesso.')
        os.remove(os.path.join(pasta,arquivo))
        print(f'{arquivo} removido com sucesso')
        extraiContaCorrenteAjustePatrimonial.extraiEntrada(arquivoSaida)