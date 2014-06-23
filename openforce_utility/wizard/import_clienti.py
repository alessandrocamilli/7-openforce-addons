# -*- encoding: utf-8 -*-
'''
Created on 06/set/2012

@author: Alessandro Camilli
'''
import xmlrpclib
import csv

if __name__ == '__main__':
    '''
    username = "admin"
    pwd = "admin"
    dbname ="glm01"
    host = 'localhost'
    '''
    username = "admin"
    pwd = "qawsed45"
    dbname ="glm02"
    host = '84.201.39.236'
    
    # Get uid
    sock_common = xmlrpclib.ServerProxy('http://' + host + ':8069/xmlrpc/common')
    uid = sock_common.login(dbname, username, pwd)
    
    #replace localhost with the address of the server
    sock = xmlrpclib.ServerProxy('http://' + host + ':8069/xmlrpc/object')
    
    
    iFile = open('export/clienti.csv', "rb")
    
    reader = csv.reader(iFile)
    partner = {}
    partner2 = {}
    partners = []
    rownum = 0
    for row in reader:
        
        #print row
        
        # Save header row.
        if rownum == 0:
            header = row
        else:
            colnum = 0
            
            partner2 = partner.copy()
            for col in row:
                idPartner = rownum -1
                field = header[colnum]
                partner2[field] = col
                
                colnum += 1
        
            partners.append(partner2)
                
        rownum += 1
    
        # Create parner se ancora non ci sono (lo vedo dalla partita iva)
    
    for cliente in partners:
        
        ##if cliente['CFCODICE'] != '2' and cliente['CFCODICE'] != '1' and cliente['CFCODICE'] != '4':
        # salto cliente già entrato
        args = [('ref', '=', cliente['codice']), ('customer', '=', 'True')]
        clienti_esistenti_ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', args)
        if len(clienti_esistenti_ids) > 0:
            continue
        
        args = [('fiscalcode', '=', cliente['codfis']), ('customer', '=', 'True')]
        clienti_esistenti_ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', args)
        if len(clienti_esistenti_ids) > 0:
            continue
       
        if cliente['partiva'] == 'PRIVATO' or cliente['codice'] in ['287', '301', '428', '666', '696', '1030', '1472', '1566', '2507', '2555' ]:
            cliente['partiva'] = '00000000000'
        
        # Controllo lunghezza partita iva per aggiungere gli zeri iniziali
        lunghezzaPartitaIva = len(cliente['partiva'])
        if lunghezzaPartitaIva < 11:
            zeriDaAggiungere = 11 - lunghezzaPartitaIva
            indice = 0
            while indice < zeriDaAggiungere:
                cliente['partiva'] = '0' + cliente['partiva']
                indice = indice +1
        
        ricercaPartitaIva = 'IT' + cliente['partiva'] + '%'
        #args = [('vat', 'like', ricercaPartitaIva)]
        args = [('ref', 'like', cliente['codice']), ('customer', '=', 'True')]
        cliente_ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', args)
        
        #cliente_data = sock.execute(dbname, uid, pwd, 'res.partner', 'read', cliente_ids) #ids is a list of id
            
        # per ora cancello il partner che trovo gia'
        #if cliente_data:
        if len(cliente_ids) > 0:
            result = sock.execute(dbname, uid, pwd, 'res.partner', 'unlink', cliente_ids)
            cliente_data = False
        
        # partitaIva
        #if cliente['codice'] != '8':
        #    continue
        #    xx='prova x debug'
            
        partitaIva =''
        if cliente['partiva'] != '00000000000':
            partitaIva =  'IT' + cliente['partiva']
            
        # Consegna
        '''
        consegna_id =''
        consegna_nome =''
        if cliente['CFCPORTO'] == 'AS':
            consegna_nome = 'ASSEGNATO'
        if cliente['CFCPORTO'] == 'FR':
            consegna_nome = 'FRANCO'
        if cliente['CFCPORTO'] == 'FA':
            consegna_nome = 'ADDEBITO'
        
        if consegna_nome != '':
            args = [('name', 'like', consegna_nome)]
            consegna_ids = sock.execute(dbname, uid, pwd, 'stock.picking.carriage_condition', 'search', args)
            consegne = sock.execute(dbname, uid, pwd, 'stock.picking.carriage_condition', 'read', consegna_ids)
            consegna_id = consegne[0]['id']
            
        # Causale del trasporto
        causale_trasporto_id =''
        causale_trasporto_nome ='VENDITA'
        
        args = [('name', '=', causale_trasporto_nome)]
        causale_trasporto_ids = sock.execute(dbname, uid, pwd, 'stock.picking.transportation_reason', 'search', args)
        causale_trasporto = sock.execute(dbname, uid, pwd, 'stock.picking.transportation_reason', 'read', causale_trasporto_ids)
        causale_trasporto_id = causale_trasporto[0]['id']
        '''
        #
        # Dati cliente
        #
        if cliente['codfis'].strip() != "":
            partnerOE = {
                    'name': cliente['ragsoc'],
                    'lang': 'it_IT',
                    'ref' : cliente['codice'],
                    'vat' : partitaIva,
                    'fiscalcode' : cliente['codfis'].strip(),
                    'street': cliente['indiriz'],
                    'zip': cliente['cap'],
                    'city': cliente['citta'],
                    'phone': cliente['numtelef'],
                    'fax': cliente['numfax'],
                    'mobile': cliente['numcell'],
                    #'province': cliente['provin'],
                    'email' : cliente['nominemail'], 
                    'is_company' : True,
                    'customer' : True
                    }
        else:
            partnerOE = {
                    'name': cliente['ragsoc'],
                    'lang': 'it_IT',
                    'ref' : cliente['codice'],
                    'vat' : partitaIva,
                    ###'fiscalcode' : cliente['codfis'].strip(),
                    'street': cliente['indiriz'],
                    'zip': cliente['cap'],
                    'city': cliente['citta'],
                    'phone': cliente['numtelef'],
                    'fax': cliente['numfax'],
                    'mobile': cliente['numcell'],
                    #'province': cliente['provin'],
                    'email' : cliente['nominemail'], 
                    'is_company' : True,
                    'customer' : True
                    } 
        partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', partnerOE)
        print cliente['codice'] + ' - ' + cliente['ragsoc']
        #
        # Contatto 
        #
        if cliente['nominativo']!= '':
            contact = {
                'name': cliente['nominativo'],
                'parent_id': partner_id,
                'phone': cliente['nomintel'],
                'fax': cliente['nominfax'],
                'mobile': cliente['nomincel'],
                #'province': cliente['CFPROVIN'],
                'email' : cliente['nominemail'],
                'customer' : True
                }
            contact_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', contact)
            print 'CONTATTO :' + cliente['codice'] + ' - ' + cliente['ragsoc']
        

        #
        # Banca
        '''
        cliente_iban = cliente['CF__IBAN']
        if cliente_iban[:2] == 'IT':
            
            # trovo id banca da abi e cab ricavati dall'iban
            abi = cliente_iban[5:10]
            cab = cliente_iban[10:15]
            args = [('abi', '=', abi), ('cab', '=', cab)]
            bank_ids = sock.execute(dbname, uid, pwd, 'res.bank', 'search', args)
            if len(bank_ids) > 0:
                
                bank_dati = sock.execute(dbname, uid, pwd, 'res.bank', 'read', bank_ids) #ids is a list of id
                
                banca = {
                    'partner_id' : partner_id,
                    'bank' : bank_dati[0]['id'],
                    'acc_number' : cliente_iban,
                    'bank_abi' : bank_dati[0]['abi'],
                    'bank_cab' : bank_dati[0]['cab'],
                    'bank_name' : bank_dati[0]['name'],
                    'state' : 'bank', # no 'iban' altrimenti chiede il codice BIC della banca
                }
                banca_id = sock.execute(dbname, uid, pwd, 'res.partner.bank', 'create', banca)
        '''
    iFile.close()
pass