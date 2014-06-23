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
import psycopg2
from StringIO import StringIO


class wizard_import_product_from_db(osv.osv_memory):
    
    _name = "wizard.import.product.from.db"
    
    _description = 'Use this wizard to import products from another db'

    _columns={
        'database_host': fields.char('Database host', size=64),
        'database_name': fields.char('Database name', size=64, select=True),
        'database_user': fields.char('Database user', size=64),
        'database_password': fields.char('Database password', size=64),
    }
    _default ={
        'database_host': 'localhost',
        'database_name': 'glm01',
        'database_user': 'openerp',
        'database_password': 'qawsed45',
    }
    
    def import_products(self, cr, uid, ids, data, context=None):
        
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            
            data['form']['database_host'] = wiz_obj['database_host']
            data['form']['database_name'] = wiz_obj['database_name']
            data['form']['database_user'] = wiz_obj['database_user']
            data['form']['database_password'] = wiz_obj['database_password']
        
        # Connection to source
        conn_string = "dbname='"+ wiz_obj['database_name'] + "' user='"+ wiz_obj['database_user'] + "' host='"+ wiz_obj['database_host'] + "' password='"+ wiz_obj['database_password'] + "'"
        try:
            #conn = psycopg2.connect("dbname='"+ data['database_name'] + "' user='"+ data['database_user'] + "' host='"+ data['database_host'] + "' password='"+ data['database_password'] + "'")
            conn = psycopg2.connect(conn_string)
        except:
            raise "I am unable to connect to the database"
        cr_origin = conn.cursor()
        
        #
        # Supplier
        #
        cr_origin.execute("""SELECT  name,id,ref FROM res_partner WHERE supplier=True """)
        suppliers_origin = cr_origin.fetchall()
        
        suppliers ={}
        for sup in suppliers_origin:
            cr.execute('SELECT  name,id,ref FROM res_partner where name =%s and supplier=True', (sup[0],) ) 
            sup_exists = cr.fetchall()
            if len(sup_exists) == 0:
                sup_OE = {
                          'name' : sup[0],
                          'lang': 'it_IT',
                          'ref' : sup[2],
                          'supplier': True,
                          'customer': False,
                          }
                
                try:
                    id_supplier = self.pool.get('res.partner').create(cr, uid, sup_OE)
                    suppliers[sup[0]] = id_supplier
                    cr.commit()
                except Exception:
                    raise ("error supplier_info creating %s", (name,))
            else:
                suppliers[sup[0]] = sup_exists[0][1]
        
        #
        # category
        #
        cr_origin.execute("""SELECT  name FROM product_category """)
        categories_origin = cr_origin.fetchall()
        
        categories ={}
        for cat in categories_origin:
            cr.execute('SELECT  name,id FROM product_category where name =%s', (cat[0],) ) 
            cat_exists = cr.fetchall()
            if len(cat_exists) == 0:
                cat_OE = {'name' : cat[0],}
                id_category = self.pool.get('product.category').create(cr, uid, cat_OE)
                categories[cat[0]] = id_category
                print cat[0]
            else:
                categories[cat[0]] = cat_exists[0][1]
        
        #
        # product
        #
        cr_origin.execute("""SELECT 
            default_code, name_template, p.ean13, pt.categ_id AS categ_id, uom_id, uom_po_id, standard_price, list_price, p.image_medium,
            ct.name AS categ_name, si.name as supplier_id, pls.price as price_sup, par.name as partner_name
            from product_product p
            left join product_template pt ON product_tmpl_id = pt.id
            left join product_category ct ON pt.categ_id = ct.id
            left join product_supplierinfo si ON p.id = si.product_id
            left join pricelist_partnerinfo pls ON si.id = pls.suppinfo_id
            left join res_partner par ON si.name = par.id
            order by p.id """)
        products_origin = cr_origin.fetchall()
        
        for prod in products_origin:
            # Verifico se già esiste
            cr.execute('SELECT id FROM product_product where default_code =%s', (prod[0],) )
            prod_exists = cr.fetchall()
            if len(prod_exists) == 0:
                default_code = prod[0]
                name = prod[1]
                ean13 = prod[2]
                categ_id = prod[3]
                uom_id = prod[4]
                uom_po_id = prod[5]
                standard_price = prod[6] 
                list_price = prod[7]
                image_medium = str(prod[8])
                categ_name = prod[9]
                supplier_id = prod[10]
                price_sup = prod[11]
                partner_name = prod[12]
                
                prod_OE = {
                    'name': name,
                    'default_code' : default_code,
                    'ean13' : ean13,
                    'type': 'product',
                    'procure_method': 'make_to_order',
                    'supply_method': 'buy',
                    'cost_method': 'standard',
                    #'standard_price': xxx,
                    'categ_id' : categories[categ_name],
                    'uom_id' : uom_id,
                    'uom_po_id' : uom_po_id,
                    'standard_price' : standard_price,
                    'list_price' : list_price,
                    'image_medium' : image_medium
                }
                try:
                    product_id = self.pool.get('product.product').create(cr, uid, prod_OE)
                    #cr.commit()
                except Exception:
                    #cr.rollback()
                    raise ("error creating %s", (name,))
            #   
            # Supplier of product
            #
                if supplier_id :
                    sup_info_OE = {
                                   'sequence': 1,
                                   'name': suppliers[partner_name],
                                   'product_id' : product_id,
                                   'product_code' : default_code,
                                   'min_qty': 0,
                                   }
                    try:
                        supplier_info_id = self.pool.get('product.supplierinfo').create(cr, uid, sup_info_OE)
                    except Exception:
                        raise ("error supplier_info creating %s", (name,))
            #
            # Price list supplier
            #
                    priceListSupplier_OE = {
                        'suppinfo_id': supplier_info_id,
                        'price': price_sup,
                        'min_quantity': 0,
                    }
                    try:
                        price_list_supplier_id = self.pool.get('pricelist.partnerinfo').create(cr, uid, priceListSupplier_OE)
                    except Exception:
                        raise ("error price list supplier creating %s", (name,))   
                
                cr.commit()

        return {'type': 'ir.actions.act_window_close'}
    
wizard_import_product_from_db()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: