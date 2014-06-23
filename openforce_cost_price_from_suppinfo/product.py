# -*- coding: utf-8 -*-
#################################################################################
#    Autor: Alessandro Camilli a.camilli@yahoo.it
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

from osv import fields, orm
import openerp.addons.decimal_precision as dp
from tools.translate import _

class product_product(orm.Model):
    
    _inherit = 'product.product'
    
    def update_price_cost_from_suppierinfo(self, cr, uid, ids, context=None):
        res=False
        for product in self.browse(cr, uid, ids):
            price_cost = 0
            supp_ids = self.pool.get('product.supplierinfo').search(cr, uid, [('product_id', '=', product.id)], order='sequence', limit=1, context=context)
            for supplierinfo in self.pool.get('product.supplierinfo').browse(cr, uid, supp_ids):
                for line in supplierinfo.pricelist_ids:
                    if not line.discount1:
                        pricelist_id = line.suppinfo_id.name.property_product_pricelist_purchase.id
                        qty = 1.0
                        pricelist_item = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], line.suppinfo_id.product_id.id, qty, line.suppinfo_id.name.id)
                        pricelist_item_id = pricelist_item['item_id'][pricelist_id]
                        price_item = self.pool.get('product.pricelist.item').browse(cr, uid, pricelist_item_id, context=context)
                        line.discount1 = price_item.discount_line
                        line.discount2 = price_item.discount2_line
                    price_cost = line.price * (1 - (line.discount1 or 0.0) / 100.0) * (1 - (line.discount2 or 0.0) / 100.0)
                    break
                # Update product cost price
                if price_cost:
                    val = {'standard_price': price_cost}
                    try:
                        self.pool.get('product.template').write(cr, uid, [product.product_tmpl_id.id], val)
                        res = True
                    except ValueError:
                        res = False
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_product, self).write(cr, uid, ids, vals, context=context)
        res_cost = self.update_price_cost_from_suppierinfo(cr, uid, ids)
        return res
    
    def create(self, cr, uid, data, context=None):
        product_id = super(product_product, self).create(cr, uid, data, context)
        
        product = self.browse(cr, uid, product_id)
        for supplierinfo in product.seller_ids:
            for line in supplierinfo.pricelist_ids:
                # l'unico modo x valorizzare discount1 e discount2 in pricelist.partnerinfo in caso di nuovo prodotto
                self.pool.get('pricelist.partnerinfo').write(cr, uid, [line.id], {}, context=context)
        
        res = self.update_price_cost_from_suppierinfo(cr, uid, [product_id])
        return product_id  

class pricelist_partnerinfo(orm.Model):
    _inherit = 'pricelist.partnerinfo'
  
    def _get_discount(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for partnerinfo in self.browse(cr, uid, ids):
            pricelist = partnerinfo.suppinfo_id.name.property_product_pricelist_purchase.id
            product = partnerinfo.suppinfo_id.product_id.id
            partner = partnerinfo.suppinfo_id.name
            qty = 1.0
            if product:
                pricelist_item = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], product, qty or 1.0, partner.id)
                pricelist_item_id = pricelist_item['item_id'][pricelist]
                price_item = self.pool.get('product.pricelist.item').browse(cr, uid, pricelist_item_id, context=context)
                if field_name == 'discount2':
                    res[partnerinfo.id] = price_item.discount2_line
                else:
                    res[partnerinfo.id] = price_item.discount_line
        return res
    
    _columns = {
        'discount1': fields.function(_get_discount, string='Discount 1', digits_compute= dp.get_precision('Account'), store=True),
        'discount2': fields.function(_get_discount, string='Discount 2', digits_compute= dp.get_precision('Account'), store=True),
        }
 
    