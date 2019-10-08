import os
import bancoMSC

#Recebe uma lista contendo dicionários com as entradas da MSC, valida contra os domínios buscados e insere os registros
#na respectiva tabela fato

def extraiEntrada(balancete, registros, arquivo, db, dimensoes, erros):

    contador = {True:0, False:0}

    for i in balancete:
        
        dimensaoPcasp = dimensoes[0]
        dimensaoDemais = dimensoes[1]
        
        seq = db.proxSequencia('SEQ_FATO_MSC')
        vLnc = int(i["lineNumberCounter"])
        vAmount = float(i["amount"])
        vBalance = i["debitCreditCode"].strip()
        vIdent = int(i["identifier"].split('EX')[0])
        vChave = int(i["chave_sk"])
        vAtualizacao = i["atualizacao"]
        vInclude = i["xbrlInclude"].strip()
        vTipoMatriz = i["tipo_msc"]

        vData = i["instant"]
        vMes = str(vData)[5:7]
        vAno = int(str(vData)[0:4])
        
        poderOrgao = i.get('PO', '')
        if poderOrgao != '':
                vPO = -9 if int(poderOrgao[:5]) not in dimensaoDemais['DIM_PODER_ORGAO'] else int(poderOrgao[:5])
        else:
                vPO = ''

        fonteRecursos = i.get('FR', '')
        if fonteRecursos != '':
                vFR = fonteRecursos[:8]
                vAnoFonte = -9 if int(vFR[0:1]) not in dimensaoDemais['DIM_ANO_FONTE_RECURSOS'] else int(vFR[0:1])
                vCodFonte = -9 if vFR[1:] not in dimensaoDemais['DIM_FONTE_RECURSOS'] else vFR[1:]
        else:
                vFR = vAnoFonte = vCodFonte = ''
        
        vAccount = -9 if i["accountMainID"][:9] not in dimensaoPcasp[vAno] else i["accountMainID"][:9]
        
        vClasse = int(i["classe"]) # Teste da classe de conta para definir o sql e pesquisar subcontas específicas
        vSubtitulo = '' if vAccount == -9 else i["accountMainID"][4]

        vPeso = -1 if ((vClasse % 2 == 0 and vBalance == 'D') or (vClasse % 2 != 0 and vBalance == 'C')) else 1

        dicionarioComum = {":sequencia": seq, ":po": vPO, ":pcasp": vAccount, ":anref": vAno, ":tipoval": vInclude, ":ente": vIdent, 
                        ":valor": vAmount, ":peso": vPeso, ":classe": vClasse, ":coleta": vChave, ":dtref": vData, ":meref": vMes, 
                        ":dtatual": vAtualizacao, ":lnc": vLnc, ":natconta": vBalance, ":tipomsc": vTipoMatriz }

        if vClasse in [1, 2, 3, 4]:
                
                financeiroPermante = i.get('FP', '')
                if financeiroPermante != '':
                        vFP = -9 if int(financeiroPermante[:1]) not in dimensaoDemais['DIM_SUPERAVIT_FINANCEIRO'] else int(financeiroPermante[:1])
                else:
                        vFP = ''
                
                dividaConsolidada = i.get('DC', '')
                
                if dividaConsolidada != '':
                        vDC = -9 if int(dividaConsolidada[:1]) not in dimensaoDemais['DIM_DIVIDA_CONSOLIDADA'] else int(dividaConsolidada[:1])
                else:
                        vDC = ''

                sql = """INSERT INTO FATO_MSC_PATRIMONIAL(ID_FATO_P, ID_DIM_PO, ID_DIM_FP, ID_DIM_ANO_FR,
                        ID_DIM_FR, ID_DIM_DC, ID_DIM_PCASP, AN_REFERENCIA, ID_DIM_TV, ID_DIM_ENTE, CO_TIPO_MATRIZ, VA_CONTABIL,
                        OP_PESO, IN_CLASSE_CONTA, ID_COLETA, DT_REFERENCIA, ME_REFERENCIA, DT_ATUALIZACAO,
                        ID_ENTRADA_MSC, CO_NAT_CONTA, IN_SUBTITULO)
                        VALUES (:sequencia, :po, :fp, :anofr, :fr, :dc, :pcasp, :anref, :tipoval, :ente, :tipomsc, :valor, :peso,
                        :classe, :coleta, :dtref, :meref, :dtatual, :lnc, :natconta, :insubtitulo)"""
                
                dicionarioPatrimonial = {":fp": vFP, ":anofr": vAnoFonte, ":fr": vCodFonte, ":dc": vDC, ":insubtitulo":vSubtitulo}
                
                dic_sql = {**dicionarioComum, **dicionarioPatrimonial}

        else:
                naturezaReceita = i.get('NR', '')
                if naturezaReceita != '':
                        vNR = naturezaReceita[:8]
                        vCER = -9 if int(vNR[:1]) not in dimensaoDemais['DIM_CAT_ECO_RECEITA'] else int(vNR[:1])
                        vOR = -9 if int(vNR[:2]) not in dimensaoDemais['DIM_ORIGEM_RECEITA'] else int(vNR[:2])
                        vESP = -9 if int(vNR[:3]) not in dimensaoDemais['DIM_ESPECIE_RECEITA'] else int(vNR[:3])

                else:
                        vNR = vCER = vOR = vESP = ''
                
                naturezaDespesa = i.get('ND', '')
                if naturezaDespesa != '':
                        vND = naturezaDespesa[:8]
                        vCED = -9 if int(vND[0:1]) not in dimensaoDemais['DIM_CAT_ECO_DESPESA'] else int(vND[0:1])
                        vGND = -9 if int(vND[1:2]) not in dimensaoDemais['DIM_GRUPO_NAT_DESPESA'] else int(vND[1:2])
                        vMOD = '-9' if vND[2:4] not in dimensaoDemais['DIM_MOD_APLICACAO'] else vND[2:4]
                        vElemento = '-9' if vND[4:6] not in dimensaoDemais['DIM_ELEMENTO'] else vND[4:6]
                else:
                        vND = vCED = vGND = vMOD = vElemento = ''

                funcaoSubfuncao = i.get('FS', '')
                if funcaoSubfuncao != '':
                        if len(funcaoSubfuncao) == 4:
                                funcaoSubfuncao = f"0{funcaoSubfuncao}"
                        vFS = funcaoSubfuncao[:5]
                        vFuncao = '-9' if vFS[0:2] not in dimensaoDemais['DIM_FUNCAO'] else vFS[0:2]
                        vSubFuncao = '-9' if vFS[2:] not in dimensaoDemais['DIM_SUBFUNCAO'] else vFS[2:]
                else:
                        vFS = vFuncao = vSubFuncao = ''
                
                educacaoSaude = i.get('ES', '')
                if educacaoSaude != '':
                        vES = -9 if int(educacaoSaude[:1]) not in dimensaoDemais['DIM_EDUCACAO_SAUDE'] else int(educacaoSaude[:1])
                else:
                        vES = ''

                anoInscricao = i.get('AI', '')
                if anoInscricao != '':
                        vAI = int(anoInscricao[:4])
                else:
                        vAI = ''
                
                if vClasse in [5, 6]:
                        sql = """INSERT INTO FATO_MSC_ORCAMENTARIA(ID_FATO_O, ID_DIM_PO, ID_DIM_ANO_FR, ID_DIM_FR, 
                                ID_DIM_FF, ID_DIM_SF, ID_DIM_PCASP, AN_REFERENCIA, ID_DIM_ES, ID_DIM_D_CED, ID_DIM_D_GND,
                                ID_DIM_D_MA, ID_DIM_D_ED, ID_DIM_R_CER, ID_DIM_R_OR, ID_DIM_R_ES, ID_DIM_TV, ID_DIM_ENTE, 
                                CO_TIPO_MATRIZ, VA_CONTABIL, OP_PESO, IN_CLASSE_CONTA, ID_COLETA, DT_REFERENCIA, ME_REFERENCIA, 
                                DT_ATUALIZACAO, ID_ENTRADA_MSC, CO_NAT_DESPESA, CO_AI, CO_NAT_RECEITA, CO_NAT_CONTA)
                                VALUES(:sequencia, :po, :anofr, :fr, :funcao, :subfuncao, :pcasp, :anref, :educsaude, :catdesp, :gnd,
                                :modaplic, :elemento, :catrec, :origem, :especie, :tipoval, :ente, :tipomsc, :valor, :peso, :classe, :coleta, 
                                :dtref, :meref, :dtatual, :lnc, :natdesp, :anoinsc, :natrec, :natconta)"""
                
                        dicionarioOrcamentario = {":anofr": vAnoFonte, ":fr": vCodFonte, ":funcao": vFuncao, ":subfuncao": vSubFuncao,
                                                ":educsaude": vES , ":catdesp": vCED, ":gnd": vGND, ":modaplic": vMOD, 
                                                ":elemento":vElemento, ":catrec": vCER, ":origem": vOR, ":especie": vESP,
                                                ":natdesp": vND, ":anoinsc": vAI, ":natrec": vNR}

                        dic_sql = {**dicionarioComum, **dicionarioOrcamentario}

                else:
                        sql = """INSERT INTO FATO_MSC_CONTROLE(ID_FATO_C, ID_DIM_PO, ID_DIM_PCASP, AN_REFERENCIA, ID_DIM_ANO_FR,
                                ID_DIM_FR, ID_DIM_FF, ID_DIM_SF, ID_DIM_ES, ID_DIM_D_CED, ID_DIM_D_GND, ID_DIM_D_MA, ID_DIM_D_ED,
                                ID_DIM_TV, ID_DIM_ENTE, CO_TIPO_MATRIZ, VA_CONTABIL, OP_PESO, IN_CLASSE_CONTA, ID_COLETA, DT_REFERENCIA, 
                                ME_REFERENCIA, DT_ATUALIZACAO, ID_ENTRADA_MSC, CO_NAT_DESPESA, CO_AI, CO_NAT_CONTA) 
                                VALUES(:sequencia, :po, :pcasp, :anref, :anofr, :fr, :funcao, :subfuncao, :educsaude, :catdesp, :gnd,
                                :modaplic, :elemento, :tipoval, :ente, :tipomsc, :valor, :peso, :classe, :coleta, :dtref, :meref, :dtatual, 
                                :lnc, :natdesp, :anoinsc, :natconta)"""

                        dicionarioControle = {":anofr": vAnoFonte, ":fr": vCodFonte, ":funcao": vFuncao, ":subfuncao": vSubFuncao,
                                                ":educsaude": vES , ":catdesp": vCED, ":gnd": vGND, ":modaplic": vMOD, 
                                                ":elemento":vElemento, ":natdesp": vND, ":anoinsc": vAI}
                        
                        dic_sql = {**dicionarioComum, **dicionarioControle}
        
        resultado = db.insereDados(sql, dic_sql, arquivo, seq, vLnc) 
        contador[resultado]+= 1
    
    db.comita()

    print(f"Coleta:{vChave}|TipoM:{vTipoMatriz}|Ibge:{vIdent}|Data:{vData}|Sucesso:{contador[True]}|Erros:{contador[False]}|Deprezados:{erros}")
    pasta = os.environ.get('PASTA_ORIGEM')
    fpath = os.path.join(pasta, arquivo)
    os.remove(fpath)
    