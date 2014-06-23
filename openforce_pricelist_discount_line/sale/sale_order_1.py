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

class sale_order_line(orm.Model):
    
    _inherit = 'sale.order.line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * (1 - (line.discount2 or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    _columns = {
                'discount2': fields.float('Discount 2(%)', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]}),
                'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
                }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None,
            discount=0, discount2=0):
        
        #########
        #import pdb
        #pdb.set_trace()
        ##########
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        
        result['value']['discount'] = discount
        result['value']['discount2'] = discount2
        if product:
            pricelist_item = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], product, qty or 1.0, partner_id)
            pricelist_item_id = pricelist_item['item_id'][pricelist]
            price_item = self.pool.get('product.pricelist.item').browse(cr, uid, pricelist_item_id, context=context)
            result['value']['discount'] = price_item.discount_line 
            result['value']['discount2'] = price_item.discount2_line 
            
        return result  
    
sale_order_line()

class sale_order(orm.Model):
    
    _inherit = 'sale.order'
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0) * (1-(line.discount2 or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
sale_order()
