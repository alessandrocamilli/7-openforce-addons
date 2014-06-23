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

class product(osv.osv_memory):
    
    _name = "openforce.utility.product"
    
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
        
        if os.path.exists("openforce-addons/openforce_utility/product/"):
            path = "openforce-addons/openforce_utility/product/"
        else:
            path = "/home/openforce/lp/openforce-addons/openforce_utility/product/"
        
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
        #reader = csv.reader(iFile, delimiter=';')
        reader = csv.reader(iFile)
        elemento = {}
        elemento2 = {}
        elementi = []
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
                elemento2 = elemento.copy()
                for col in row:
                    idPartner = rownum -1
                    field = header[colnum]
                    elemento2[field] = col
                    colnum += 1
                elementi.append(elemento2)
            rownum += 1
        nr = 0
        
        # prima ciclo x controllare esistenza di tutti i fornitori
        partners_errati = ''
        p_err_ref = []
        for row in elementi:
            supplier_ids = self.pool.get('res.partner').search(cr, uid, [('name', 'ilike',  row['supplier_name'] +'%'), ('supplier', '=', True)])
            if not supplier_ids and row['supplier_name'] not in p_err_ref:
                partners_errati = partners_errati + " -- " + row['supplier_name']
                p_err_ref.append(row['supplier_name'])
        
        if partners_errati:
            raise osv.except_osv(_('Error!'), _('error Fornitori non trovati: %s') % (partners_errati,))
            
        #i=0
        for row in elementi:
            
            #i+=1
            #if i>100 :
            #    break
            #import pdb
            #pdb.set_trace()
            # Non importare
            if 'no_import' in row and row['no_import']:
                continue
            
            # verifico se già esiste con campo ref
            product_exist_id = False
            product_exist = self.pool.get('product.product').search(cr, uid, [('default_code', '=', row['default_code'])])
            if product_exist:
                product_exist_id = product_exist[0]
                
            '''
            SETUP
            '''
            # Supplier
            supplier_ids = self.pool.get('res.partner').search(cr, uid, [('name', 'ilike',  row['supplier_name'] +'%'), ('supplier', '=', True)])
            if not supplier_ids:
                #raise ("error Fornitore non trovato: %s", (row['supplier_name']))
                raise osv.except_osv(_('Error!'), _('error Fornitore non trovato: %s') % (row['supplier_name'],))
            supplier = self.pool.get('res.partner').browse(cr, uid, supplier_ids[0])
            
            price = float(row['price'].replace(',', '.'))
            supplier_cost = float(row['supplier_cost'].replace(',', '.'))
            
            # Costo for
            supp_cost = {'min_quantity' : 0, 'price' : supplier_cost}
            supp_info = {
                 'name' : supplier.id,
                 'product_code' : row['supplier_product_code'],
                 'min_qty' : 0,
                 'pricelist_ids' : [(0, 0, supp_cost)]
                 }
            vals ={
                'name': row['name'],
                'default_code': row['default_code'],
                'uom_id': data['form']['uom_id'][0],
                'list_price': price,
                #1'standard_price': float(row['supplier_cost']),
                'standard_price': supplier_cost,
                'seller_ids': [(0, 0, supp_info)],
                }
            nr += 1
            print str(nr) + '->' + row['default_code'] + '--' + row['name']
            if not product_exist_id:
                product_id = self.pool.get('product.product').create(cr, uid, vals)
            else:
                # delete all supplierinfo linked
                pr = self.pool.get('product.product').browse(cr, uid, product_exist_id)
                try:
                    if pr.seller_ids:
                        supp_inf_ids = self.pool.get('product.supplierinfo').search(cr, uid, [('product_id', '=', pr.id)])
                        self.pool.get('product.supplierinfo').unlink(cr, uid, supp_inf_ids)
                
                    self.pool.get('product.product').write(cr, uid, [product_exist_id] ,vals)
                except Exception:
                    print 'ERROR'
            
        iFile.close()
        
    def default_code_from_supplier_code(self, cr, uid, ids, data, context=None):
        nr = 0
        product_ids = self.pool.get('product.product').search(cr, uid, [('id', '!=', False)])
        for product in self.pool.get('product.product').browse(cr, uid, product_ids):
            new_default_code = False
            nr += 1
            if product.default_code :
                print str(nr) + '->' + product.default_code + '--' + product.name
            else:
                print str(nr) + '->' + '--' + product.name
                
            if product.type == 'service':
                continue
            if product.seller_ids:
                new_default_code = product.seller_ids[0]['product_code']
                self.pool.get('product.product').write(cr, uid, [product.id], {'default_code' : new_default_code})
        
            
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: