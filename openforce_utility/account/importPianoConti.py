# -*- encoding: utf-8 -*-
'''
Created on 06/set/2012

@author: Alessandro Camilli
'''
import xmlrpclib
import csv


class ImportPianoConti:

    _username = "admin"
    _pwd = "admin"
    _dbname ="demo02"
    
    _host = 'localhost'
    '''
    _username = "admin"
    _pwd = "ASDzxc191074"
    _dbname ="az05"
    
    _host = '79.4.198.41'
    '''
        
    def readFromCsv(self=None):
        
        iFile = open('export/pianoDeiConti.csv', "rb")
        
        reader = csv.reader(iFile, delimiter=';')
        partner = {}
        partner2 = {}
        partners = []
        rownum = 0
        for row in reader:
            
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
            
        iFile.close()
        return partners
    
    
    if __name__ == '__main__':
        
        # Get uid
        sock_common = xmlrpclib.ServerProxy('http://' + _host + ':8069/xmlrpc/common')
        uid = sock_common.login(_dbname, _username, _pwd)
        
        #replace localhost with the address of the server
        sock = xmlrpclib.ServerProxy('http://' + _host + ':8069/xmlrpc/object')
        
        datiFromCsv = readFromCsv()
        
        
        for conto in datiFromCsv:
            
            prova = conto['piacod'][4:] # da posiz. 4 alla fine
            
            ## CONTO top PICENIA
            args = [('code', '=', '0000000')]
            conti_ids = sock.execute(_dbname, uid, _pwd, 'account.account', 'search', args)
            
            conto_root_id = 0
            if len(conti_ids) > 0:
                conto_root = sock.execute(_dbname, uid, _pwd, 'account.account', 'read', conti_ids)
                conto_root_id = conto_root[0]['id']
                
            if conto_root_id == 0:
                
                # type
                user_type_id =''
                user_type_code ='view'
                
                if user_type_code != '':
                    args = [('code', 'like', user_type_code)]
                    user_type_ids = sock.execute(_dbname, uid, _pwd, 'account.account.type', 'search', args)
                    user_type = sock.execute(_dbname, uid, _pwd, 'account.account.type', 'read', user_type_ids)
                    user_type_id = user_type[0]['id']
                
                contoOE = {
                        'name': 'Azienda',
                        'code' : '0000000',
                        'level' : 0,
                        'reconcile' : False,
                        'type': 'view',
                        'user_type': user_type_id,
                        }
                conto_root_id = sock.execute(_dbname, uid, _pwd, 'account.account', 'create', contoOE)
                #continue
            
            ## CONTO vista
            
            if conto['piacod'][4:] == '000':
                
                # vedo se esiste
                conto_view_id = 0
                args = [('code', '=', conto['piacod'])]
                conti_ids = sock.execute(_dbname, uid, _pwd, 'account.account', 'search', args)
                if len(conti_ids) > 0:
                    conto_view = sock.execute(_dbname, uid, _pwd, 'account.account', 'read', conti_ids)
                    conto_view_id = conto_view[0]['id']
                
                if conto_view_id == 0:
                    
                    # livello
                    level = 2
                    if conto['piacod'][3:] == '0000':
                        level = 1
                    
                    # parent_id
                    parent_id = 0
                    if conto['piacod'][3:] == '0000':
                        parent_id = conto_root_id
                    else:
                        conto_padre = conto['piacod'][:3] + '0000'
                        args = [('code', '=', conto_padre)]
                        conti_ids = sock.execute(_dbname, uid, _pwd, 'account.account', 'search', args)
                        if len(conti_ids) > 0:
                            conto_parent = sock.execute(_dbname, uid, _pwd, 'account.account', 'read', conti_ids)
                            parent_id = conto_parent[0]['id']
                        
                    
                    # type
                    user_type_id =''
                    user_type_code ='view'
                    
                    if user_type_code != '':
                        args = [('code', 'like', user_type_code)]
                        user_type_ids = sock.execute(_dbname, uid, _pwd, 'account.account.type', 'search', args)
                        user_type = sock.execute(_dbname, uid, _pwd, 'account.account.type', 'read', user_type_ids)
                        user_type_id = user_type[0]['id']
                        
                    contoOE = {
                            'name': conto['piades'],
                            'code' : conto['piacod'],
                            'level' : level,
                            'reconcile' : True,
                            'type': 'view',
                            'user_type': user_type_id,
                            'parent_id': parent_id,
                            }
                    
                    conto_view_id = sock.execute(_dbname, uid, _pwd, 'account.account', 'create', contoOE)
                continue
            
            ## CONTO normale
            
            if conto['piacod'][4:] != '000':
                
                # vedo se esiste
                
                conto_normale_id = 0
                args = [('code', '=', conto['piacod'])]
                conti_ids = sock.execute(_dbname, uid, _pwd, 'account.account', 'search', args)
                if len(conti_ids) > 0:
                    conto_normale = sock.execute(_dbname, uid, _pwd, 'account.account', 'read', conti_ids)
                    conto_normale_id = conto_normale[0]['id']
                
                if conto_normale_id == 0:
                    
                    # parent id
                    args = [('code', '=', conto['piacod'][:4] + '000')]
                    conti_ids = sock.execute(_dbname, uid, _pwd, 'account.account', 'search', args)
                    if len(conti_ids) > 0:
                        conto_parent = sock.execute(_dbname, uid, _pwd, 'account.account', 'read', conti_ids)
                        conto_parent_id = conto_parent[0]['id']
                    
                    # type
                    type = ''
                    type = 'other'
                    
                    # user type
                    user_type_id =''
                    user_type_code = ''
                    reconcile = True
                    if conto['piasez'] == 'A' and user_type_code =='':
                        user_type_code ='asset'
                    if conto['piasez'] == 'P' and user_type_code =='':
                        user_type_code ='payable'
                    if conto['piasez'] == 'C' and user_type_code =='':
                        user_type_code ='expense'
                    if conto['piasez'] == 'R' and user_type_code =='':
                        user_type_code ='income'
                    if conto['piasez'] == 'O' and user_type_code =='':
                        user_type_code ='liability'
                    
                    if user_type_code != '':
                        args = [('code', 'like', user_type_code)]
                        user_type_ids = sock.execute(_dbname, uid, _pwd, 'account.account.type', 'search', args)
                        user_type = sock.execute(_dbname, uid, _pwd, 'account.account.type', 'read', user_type_ids)
                        user_type_id = user_type[0]['id']
                    
                    print conto['piacod'] + ' ' + conto['piades']
                    contoOE = {
                            'name': conto['piades'],
                            'code' : conto['piacod'],
                            'level' : 3,
                            'reconcile' : reconcile,
                            'type': type,
                            'user_type': user_type_id,
                            'parent_id': conto_parent_id,
                            }
                    
                    conto_normale_id = sock.execute(_dbname, uid, _pwd, 'account.account', 'create', contoOE)
                
            # Controllo lunghezza partita iva per aggiungere gli zeri iniziali
        
        
    #pass