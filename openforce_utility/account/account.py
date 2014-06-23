# -*- coding: utf-8 -*-
#################################################################################
#    Author: Alessandro Camilli a.camilli@yahoo.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv
from tools.translate import _
import time
import base64
import csv
import os
import re
class account(osv.osv_memory):
    
    _name = "openforce.utility.account"
    
    _description = 'Use this wizard to work with charts'
    
    def import_from_csv(self, cr, uid, ids, data, context=None):
        '''
        convenzioni:
        le intestaizione dii colonne devono essere le stesse dei campi di OE
        
        COLONNA no_import:
        se non è vuota, non importa l'elemento. Ci si scrive la motivazione per cui il record
        non va importato
        '''
        
        file_txt_to_import = base64.decodestring(data['form']['file_txt_to_import'])
        
        if os.path.exists("openforce-addons/openforce_utility/partner/"):
            path = "openforce-addons/openforce_utility/partner/"
        else:
            path = "/home/openforce/lp/openforce-addons/openforce_utility/partner/"
        
        f = open( path + "file_txt_to_import.csv", "w")
        f.write(file_txt_to_import)
        f.close()
        #----------------------------------------------
        # Setup Cols
        #----------------------------------------------
        #iFile = open('openforce-addons/openforce_utility/partner/file_txt_to_import.csv', "rb")
        iFile = open( path + "file_txt_to_import.csv", "rb")
        #reader = iFile.readlines()
        #reader = csv.reader(iFile, delimiter=';')
        reader = csv.reader(iFile)
        partner = {}
        partner2 = {}
        partners = []
        rownum = 0
        for row in reader:
            #import pdb
            #pdb.set_trace()
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
        
        #----------------------------------------------
        # Import
        #----------------------------------------------
        #solo_2_clienti = 0
        for row in partners:
            account_account_obj = self.pool['account.account']
            account_account_type_obj = self.pool['account.account.type']
            # Non importare
            if 'no_import' in row and row['no_import']:
                continue
            
            # Remove special char
            setup_code = row['code']
            if data['form']['code_leaving_number_letter']:
                setup_code = re.sub('[^A-Za-z0-9]+', '', setup_code)
            
            # verifico se già esiste con campo codice
            account_exist_id = False
            account_exist = account_account_obj.search(cr, uid, [('code', '=', row['code'])])
            if account_exist:
                account_exist_id = account_exist[0]
            
            # Is view?
            account_is_view = False
            if len(setup_code) <= data['form']['code_length_max_view']:
                account_is_view = True
            
            # Parent
            account_parent_id = False
            if account_is_view:
                lenght_code_parent = len(setup_code) / data['form']['code_length_sub_account']
            else:
                lenght_code_parent = data['form']['code_length_max_view']
            code_parent = setup_code[:lenght_code_parent]
            account_parent_ids = account_account_obj.search(cr, uid, [('code', '=', code_parent)])
            if account_parent_ids:
                account_parent_id = account_parent_ids[0]
            
            # Type
            setup_type = "other"
            if account_is_view:
                setup_type = "view"
            
            # User_type --> Default
            # Attivita
            if setup_code[:2] in ('00', '01', '02'):
                domain = [('name', '=', 'Asset')]
                account_user_type_ids = account_account_type_obj.search(cr, uid, domain, limit=1)
                if account_user_type_ids:
                    setup_user_type_id = account_user_type_ids[0]
                # Crediti
                #if not account_is_view and setup_code[:2] in ('02',):
                #    setup_type = "receivable"
            elif setup_code[:2] in ('03', '04', '05', '06'):          
                domain = [('name', '=', 'Liability')]
                account_user_type_ids = account_account_type_obj.search(cr, uid, domain, limit=1)
                if account_user_type_ids:
                    setup_user_type_id = account_user_type_ids[0]
            elif setup_code[:2] in ('07',):
                domain = [('name', '=', 'Expense')]
                account_user_type_ids = account_account_type_obj.search(cr, uid, domain, limit=1)
                if account_user_type_ids:
                    setup_user_type_id = account_user_type_ids[0]
            elif setup_code[:2] in ('08',):
                domain = [('name', '=', 'Income')]
                account_user_type_ids = account_account_type_obj.search(cr, uid, domain, limit=1)
                if account_user_type_ids:
                    setup_user_type_id = account_user_type_ids[0]
            else:
                domain = [('name', '=', 'Root/View')]
                account_user_type_ids = account_account_type_obj.search(cr, uid, domain, limit=1)
                if account_user_type_ids:
                    setup_user_type_id = account_user_type_ids[0]
                    
            
            account_exists = account_account_obj.search(cr, uid, [('code', '=', setup_code)])
            
            print row['code'] + ' ' + row['name']
            val = {
                'name': row['name'],
                'code' : setup_code,
                #'level' : 3,
                'reconcile' : True,
                'type': setup_type,
                'user_type': setup_user_type_id,
                'parent_id': account_parent_id,
                }
            
            
            if account_exists:
                account_account_obj.write(cr, uid,[account_exists[0]], val)
            else:
                account_account_obj.create(cr, uid, val)
            
        iFile.close()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: