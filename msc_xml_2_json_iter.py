import xml.etree.ElementTree as ET
import json

contexto = ['{http://www.xbrl.org/2003/instance}identifier','{http://www.xbrl.org/2003/instance}instant']
fatos = ['{http://www.xbrl.org/int/gl/cor/2015-03-25}lineNumberCounter', '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountMainID', '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountMainDescription', '{http://www.xbrl.org/int/gl/cor/2015-03-25}amount', '{http://www.xbrl.org/int/gl/cor/2015-03-25}signOfAmount', '{http://www.xbrl.org/int/gl/cor/2015-03-25}debitCreditCode', '{http://www.xbrl.org/int/gl/cor/2015-03-25}xbrlInclude']
subcontas = ['{http://www.xbrl.org/int/gl/cor/2015-03-25}accountSubID', '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountSubType', '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountSubDescription']
entryDetail = '{http://www.xbrl.org/int/gl/cor/2015-03-25}entryDetail'
accountSub = '{http://www.xbrl.org/int/gl/cor/2015-03-25}accountSub'
balancete = []
contx = {}

xml_iter = ET.iterparse('instancia.xml', events=('start','end'))

for event, elem in xml_iter:
	elemento = str(elem.tag).split("}",1)[1]
	dicionario = [elemento, elem.text] 
	
	if event == 'end' and elem.tag in contexto: # verifica as tags de ente e periodo
		contx[str(dicionario[0])] = dicionario[1]
	elif event == 'start' and elem.tag == entryDetail: #verifica se um entryDetail foi aberto
		fatx = {}
		subac = []
	elif event == 'start'and elem.tag == accountSub: #verifica se está passando uma subconta
		subdic = {}
	elif event == 'end' and elem.tag in subcontas: #verifica se está fechando uma conta corrente
		subdic[str(dicionario[0])] = dicionario[1]	
	elif event == 'end' and elem.tag == accountSub:
		subac.append(subdic)
	elif event == 'end' and elem.tag in fatos: #verifica se o elemento listado está no array de fatos desejados
		if elemento == 'amount':
			fatx[str(dicionario[0])] = float(dicionario[1])
		else:
			fatx[str(dicionario[0])] = dicionario[1]
	elif event == 'end' and elem.tag == entryDetail: #verifica se o entryDetail foi fechado
		fatx['accountSub'] = subac
		subac = []
		fatx.update(contx)
		balancete.append(fatx)
		
#print(balancete)

with open('msc_iter.json', 'w') as fp:
	json.dump(balancete, fp, indent=4)
