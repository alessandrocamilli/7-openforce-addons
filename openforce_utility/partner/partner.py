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

class partner(osv.osv_memory):
    
    _name = "openforce.utility.partner"
    
    _description = 'Use this wizard to work with partners'
    
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
        
        #f = open("openforce-addons/openforce_utility/partner/file_txt_to_import.csv", "w")
        f = open( path + "file_txt_to_import.csv", "w")
        f.write(file_txt_to_import)
        f.close()
        #
        # Setup Cols
        #
        #iFile = open('openforce-addons/openforce_utility/partner/file_txt_to_import.csv', "rb")
        iFile = open( path + "file_txt_to_import.csv", "rb")
        #reader = iFile.readlines()
        if data['form']['field_separator_csv'][:1] == ';':
            reader = csv.reader(iFile, delimiter=';')
        else:
            reader = csv.reader(iFile)
        #reader = csv.reader(iFile)
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
        
        #solo_2_clienti = 0
        for row in partners:
            # Non importare
            if 'no_import' in row and row['no_import']:
                continue
            if not 'name' in row:
                continue
            
            if 'name2' in row and row['name2']:
                row['name'] += row['name2']
            
            print row['name']
            #import pdb
            #pdb.set_trace()
            # verifico se già esiste con campo ref
            partner_exist_id = False
            partner_exist = self.pool.get('res.partner').search(cr, uid, [('ref', '=', row['ref'])])
            if partner_exist:
                partner_exist_id = partner_exist[0]
                
            '''
            SETUP
            '''
            setup_is_customer = data['form']['is_customer']
            setup_is_supplier = data['form']['is_supplier']
            # vat
            #if row['ref'] == '9':
            #    import pdb
            #    pdb.set_trace()
            partner_grouped = False
            setup_vat = False
            partner_exists = False
            if row['vat']:
                #import pdb
                #pdb.set_trace()
                # aggiunta prefisso se la partita iva inizia con nr
                setup_vat = row['vat']
                if data['form']['prefisso_partita_IVA'] and row['vat'] and row['vat'][:1].isdigit():
                    p_iva = '{:11s}'.format(row['vat'].zfill(11)) 
                    setup_vat = data['form']['prefisso_partita_IVA'] + p_iva
                    
                    # Partner already exist:
                    if not partner_exists and setup_is_customer:
                        partner_exists = self.pool.get('res.partner').search(cr, uid, [('vat', '=', setup_vat),
                                                                                         ('customer', '=', True),
                                                                                         ('is_company', '=', True)])
                    if not partner_exists and setup_is_supplier:
                        partner_exists = self.pool.get('res.partner').search(cr, uid, [('vat', '=', setup_vat),
                                                                                         ('supplier', '=', True),
                                                                                         ('is_company', '=', True)])
                    
                    # group partner
                    if not partner_exists:
                        # ...importing supplier
                        if not setup_is_customer and setup_is_supplier:
                            partner_customer = self.pool.get('res.partner').search(cr, uid, [('vat', '=', setup_vat),
                                                                                             ('customer', '=', True),
                                                                                             ('is_company', '=', True)])
                            if partner_customer:
                                self.pool.get('res.partner').write(cr, uid, [partner_customer[0]] , {'supplier':True})
                                partner_grouped = True
                        # ...importing customer
                        if not setup_is_supplier and setup_is_customer:
                            partner_supplier = self.pool.get('res.partner').search(cr, uid, [('vat', '=', setup_vat),
                                                                                             ('supplier', '=', True),
                                                                                             ('is_company', '=', True)])
                            if partner_supplier:
                                self.pool.get('res.partner').write(cr, uid, [partner_supplier[0]] , {'customer':True})
                                partner_grouped = True
            if partner_exists:
                continue
            if partner_grouped == True:
                continue
            
            # fiscal_code
            partner_exists = False
            setup_fiscalcode = False
            if 'fiscalcode' in row and row['fiscalcode']:
                setup_fiscalcode = row['fiscalcode']
                if len(setup_fiscalcode) < 16:
                    setup_fiscalcode = '{:11s}'.format(row['fiscalcode'].zfill(11))
                    
                 # Partner already exist:
                if not partner_exists and setup_is_customer:
                    partner_exists = self.pool.get('res.partner').search(cr, uid, [('fiscalcode', '=', setup_fiscalcode),
                                                                                     ('customer', '=', True),
                                                                                     ('is_company', '=', True)])
                if not partner_exists and setup_is_supplier:
                    partner_exists = self.pool.get('res.partner').search(cr, uid, [('fiscalcode', '=', setup_fiscalcode),
                                                                                     ('supplier', '=', True),
                                                                                     ('is_company', '=', True)])
                # group partner
                if not partner_exists:
                    # ...importing supplier
                    if not setup_is_customer and setup_is_supplier:
                        partner_customer = self.pool.get('res.partner').search(cr, uid, [('fiscalcode', '=', setup_fiscalcode),
                                                                                         ('customer', '=', True),
                                                                                         ('is_company', '=', True)])
                        if partner_customer:
                            self.pool.get('res.partner').write(cr, uid, [partner_customer[0]] , {'supplier':True})
                            partner_grouped = True
                    # ...importing customer
                    if not setup_is_supplier and setup_is_customer:
                        # group:
                        partner_supplier = self.pool.get('res.partner').search(cr, uid, [('fiscalcode', '=', setup_fiscalcode),
                                                                                         ('supplier', '=', True),
                                                                                         ('is_company', '=', True)])
                        if partner_supplier:
                            self.pool.get('res.partner').write(cr, uid, [partner_supplier[0]] , {'customer':True})
                            partner_grouped = True
            if partner_exists:
                continue
            if partner_grouped == True:
                continue
            
            # city
            setup_city = row['city']
            setup_zip = False
            setup_province_id = False
            setup_region_id = False
            setup_country_id = False
            if(setup_city):
                city_id = self.pool.get('res.city').search(cr, uid, [('name', '=ilike', setup_city)])
                if len(city_id) == 1:
                    if city_id:
                        city_obj = self.pool.get('res.city').browse(cr, uid, city_id[0])
                        # unico cap
                        if 'x' not in city_obj.zip:
                            setup_zip = city_obj.zip
                            setup_province_id = city_obj.province_id and city_obj.province_id.id or False
                            setup_region_id = city_obj.region and city_obj.region.id or False
                            setup_country_id = city_obj.region.country_id.id or False
            # zip
            if not setup_zip and ('zip' in row):
                setup_zip = row['zip']
            # province
            if not setup_province_id and ('province' in row) and row['province']:
                province_id = self.pool.get('res.province').search(cr, uid, [('code', '=ilike', row['province'])])
                if len(province_id) == 1:
                    setup_province_id = province_id[0]
            # region
            if not setup_region_id and ('region' in row) and row['region']:
                region_id = self.pool.get('res.region').search(cr, uid, [('name', '=ilike', row['region'])])
                if len(region_id) == 1:
                    setup_region_id = region_id[0]
            # country
            if not setup_country_id and ('country' in row) and row['country']:
                country_id = self.pool.get('res.country').search(cr, uid, [('name', '=ilike', row['country'])])
                if len(country_id) == 1:
                    setup_country_id = country_id[0]
                    
            # partner_ref
            setup_is_company = True
            setup_parent_id = False
            if 'parent_id/id' in row and row['parent_id/id']:
                setup_is_company = False
                parent_id = int(row['parent_id/id'].replace('__export__.res_partner_', '0')) 
            
            print row['ref'] + ' - ' + row['name']
            print 'Partita IVA: ' + str(setup_vat)
            vals = {
                    'is_company' : setup_is_company,
                    'parent_id' : setup_parent_id,
                    'customer' : setup_is_customer,
                    'supplier' : setup_is_supplier,
                    'ref' : row['ref'],
                    'name' : row['name'],
                    'street' : 'street' in row and row['street'] or False,
                    'city' : setup_city,
                    'zip' : setup_zip,
                    'province' : setup_province_id,
                    'region' : setup_region_id,
                    'country_id' : setup_country_id,
                    'phone' : 'phone' in row and row['phone'] or False,
                    'mobile' : 'mobile' in row and row['mobile'] or False,
                    'fax' : 'fax' in row and row['fax'] or False,
                    'email' : 'email' in row and row['email'] or False,
                    'vat' : setup_vat,
                    'fiscalcode' : setup_fiscalcode,
                    }
            
            if not partner_exist_id:
                partner_id = self.pool.get('res.partner').create(cr, uid, vals)
            else:
                self.pool.get('res.partner').write(cr, uid, [partner_exist_id] ,vals)
            '''
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
                '''
            
        iFile.close()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: