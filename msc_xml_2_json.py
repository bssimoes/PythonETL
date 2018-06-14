import xml.etree.ElementTree as ET
import json

doc = ET.parse('instancia_small.xml')   # arquivo xml da instância MSC (caso o arquivo não esteja na mesma pasta de salvamento do arquivo py, colocar o caminho)
root = doc.getroot() # Elemento raiz da instância MSC
nms = {"xbrli":"http://www.xbrl.org/2003/instance", "gl-bus":"http://www.xbrl.org/int/gl/bus/2015-03-25", "gl-cor":"http://www.xbrl.org/int/gl/cor/2015-03-25", "iso4217":"http://www.xbrl.org/2003/iso4217", "link":"http://www.xbrl.org/2003/linkbase", "xlink":"http://www.w3.org/1999/xlink", "xsi":"http://www.w3.org/2001/XMLSchema-instance"} #cria dicionario de namespaces para poder usar xpath sem necessidade da URI


v_identifier = root.find('xbrli:context/xbrli:entity/xbrli:identifier',nms).text #armazena o ente
v_period = root.find('xbrli:context/xbrli:period/xbrli:instant', nms).text #armazena o periodo da msc

balancete = [] # lista vazia onde serao incluidos todos os entry details - apesar do nome ainda nao tem formato de balancete

for edetail in root.findall('./gl-cor:accountingEntries/gl-cor:entryHeader/gl-cor:entryDetail', nms): # loop em uma lista com todos os entry details da instancia   
	
	scontas = edetail.findall('gl-cor:account/gl-cor:accountSub', nms) # no entry detail especifico, encontra quantos accountSub existem
	subs = len(scontas)
	acSub = [] # lista vazia onde serao armazenados os contas correntes
	i = 1
	while i <= subs:
		v_accountSubId = edetail.find('gl-cor:account/gl-cor:accountSub[%s]/gl-cor:accountSubID' % i, nms).text
		v_accountSubType = edetail.find('gl-cor:account/gl-cor:accountSub[%s]/gl-cor:accountSubType'% i, nms).text
		v_accountSubDesc = edetail.find('gl-cor:account/gl-cor:accountSub[%s]/gl-cor:accountSubDescription'% i, nms)
		if v_accountSubDesc == None:
			cc = dict(accountSubId = v_accountSubId, accountSubType = v_accountSubType)
		else:
			v_accountSubDesc = edetail.find('gl-cor:account/gl-cor:accountSub[%s]/gl-cor:accountSubDescription'% i, nms).text
			cc = dict(accountSubDescription = v_accountSubDesc, accountSubId = v_accountSubId, accountSubType = v_accountSubType)
		acSub.append(cc) # adiciona uma conta corrente a lista final
		i += 1
	
	amainID = edetail.find('gl-cor:account/gl-cor:accountMainID', nms).text # localiza o ID da Conta 
	amnt = float(edetail.find('gl-cor:amount', nms).text) # localiza o amount
	sgoa = edetail.find('gl-cor:signOfAmount', nms).text 
	lnc = edetail.find('gl-cor:lineNumberCounter', nms).text
	dc = edetail.find('gl-cor:debitCreditCode', nms).text # localiza o debito/credito
	include = edetail.find('gl-cor:xbrlInfo/gl-cor:xbrlInclude', nms).text # localiza o include
	amainDesc = edetail.find('gl-cor:account/gl-cor:accountMainDescription', nms)
	
	if amainDesc != None:
		amainDesc = edetail.find('gl-cor:account/gl-cor:accountMainDescription', nms).text
		entryDetail = dict(identifier = v_identifier, instant = v_period, lineNumberCounter = lnc, accountMainId = amainID, accountMainDescription = amainDesc, accountSub = acSub, amount = amnt, signOfAmount = sgoa, debitCredit = dc, typeOfValue = include )
	else:
		entryDetail = dict(identifier = v_identifier, instant = v_period, lineNumberCounter = lnc, accountMainId = amainID, accountSub = acSub, amount = amnt, signOfAmount = sgoa, debitCredit = dc, typeOfValue = include )

	balancete.append(entryDetail) # adiciona a lista ao balancete

#print(balancete)
#msc= dict(identifier = v_identifier, instant = v_period, entryDetail = balancete )

#print(msc)


with open('msc.json', 'w') as fp:
	json.dump(balancete, fp, indent=4)