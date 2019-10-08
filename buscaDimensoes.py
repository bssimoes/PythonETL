import bancoMSC

# Busca os domínios das tabelas dimensionais e armazena em dois dicionários. Um para o PCASP e outro para as demais dimensões.

dicionarioDimensoes = {'DIM_ANO_FONTE_RECURSOS': 'ID_DIM_ANO_FR', 'DIM_CAT_ECO_DESPESA': 'ID_DIM_D_CED',
                        'DIM_CAT_ECO_RECEITA': 'ID_DIM_R_CER', 'DIM_DIVIDA_CONSOLIDADA': 'ID_DIM_DC',
                        'DIM_EDUCACAO_SAUDE': 'ID_DIM_ES', 'DIM_ELEMENTO': 'ID_DIM_D_ED',
                        'DIM_ESPECIE_RECEITA': 'ID_DIM_R_ES', 'DIM_FONTE_RECURSOS': 'ID_DIM_FR',
                        'DIM_FUNCAO': 'ID_DIM_FF', 'DIM_GRUPO_NAT_DESPESA': 'ID_DIM_D_GND',
                        'DIM_MOD_APLICACAO': 'ID_DIM_D_MA', 'DIM_ORIGEM_RECEITA': 'ID_DIM_R_OR',
                        'DIM_PODER_ORGAO': 'ID_DIM_PO', 'DIM_SUBFUNCAO': 'ID_DIM_SF',
                        'DIM_SUPERAVIT_FINANCEIRO': 'ID_DIM_FP', 'DIM_TIPO_MATRIZ': 'CO_TIPO_MATRIZ'} 

def buscaDimensoes():
    db = bancoMSC.Conexao()
    
    # Dimensão do PCASP armazenada em dicionário específico cuja chave é o ano de referência e seu valor é uma lista com as contas
    listaAnosPcasp = db.buscaDimensao('select distinct an_referencia from dim_pcasp_estendido')
    dicionarioPcasp = {}
    for i in listaAnosPcasp:
        dicionarioPcasp[i] = db.buscaDimensao(f'select id_dim_pcasp from dim_pcasp_estendido where an_referencia = {i}')

    # Demais dimensões armazenada em dicionário cuja chave é o nome da tabela e o valor é uma lista com o domínio.
    dicionarioDemais = {}
    for key, value in dicionarioDimensoes.items():
        
        listaDimensao = db.buscaDimensao(f'select {value} from {key}')
        
        dicionarioDemais[key] = listaDimensao
            
    db.desconectaBanco()
    return (dicionarioPcasp, dicionarioDemais)