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

class bank(osv.osv_memory):
    
    _name = "openforce.utility.bank"
    
    _description = 'Use this wizard to import bank from txt'
    
    def import_from_abicab(self, cr, uid, ids, data, context=None):
        
        import pdb
        pdb.set_trace()
        file_txt_to_import = base64.decodestring(data['form']['file_txt_to_import'])
        #file_txt_to_import = base64.encodestring(data['form']['file_txt_to_import'])
        f = open("openforce-addons/openforce_utility/bank/file_txt_to_import.txt", "w")
        f.write(file_txt_to_import)
        f.close()
        
        iFile = open('openforce-addons/openforce_utility/bank/abicab.txt')
        reader = iFile.readlines()
        
        for row in reader:
            
            prefissoRiga = row[:2]
            #
            # INTESTAZIONE BANCA
            #
            if prefissoRiga == '11':
                banca_descrizione = row[13:93]
            #
            # INDIRIZZO AGENZIA
            #
            if prefissoRiga == '21':
                agenzia_indirizzo = row[20:60]
                agenzia_localita = row[140:180]
                agenzia_cap = row[180:185]
                agenzia_provincia = row[185:187] 
            #
            # AGENZIA
            #
            if prefissoRiga == '31':
                agenzia_abi = row[2:7]
                agenzia_cab = row[7:12]
                agenzia_descrizione = row[12:52]
                
                # Creazione banca ( dopo ogni agenzia)
                bank_dati = {
                        'name': banca_descrizione.strip().decode('cp1252') + ' - ' + agenzia_descrizione.strip().decode('cp1252'),
                        'abi' : agenzia_abi,
                        'cab': agenzia_cab,
                        'street': agenzia_indirizzo.strip().decode('cp1252'),
                        'zip': agenzia_cap,
                        'city': agenzia_localita.strip().decode('cp1252'),
                        }
                
                cr.execute('SELECT  name,id FROM res_bank where abi =%s and cab=%s', (agenzia_abi, agenzia_cab) )
                bank_exists = cr.fetchall()
                if len(bank_exists) == 0:
                    try:
                        bank_id = self.pool.get('res.bank').create(cr, uid, bank_dati)
                        cr.commit()
                    except Exception:
                        cr.rollback()
                        raise ("error creating %s: abi %s, cab %s", (banca_descrizione,agenzia_abi,agenzia_cab))    
                
            
        iFile.close()
bank()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: