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
from tools.translate import _
import decimal_precision as dp

class purchase_order_line(orm.Model):
    
    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * (1 - (line.discount2 or 0.0) / 100.0)
            #taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty)
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, price, line.product_qty)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    _inherit = 'purchase.order.line'
    _columns = {
                'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Purchase Price')),
                'discount': fields.float('Discount (%)', digits=(16, 2)),
                'discount2': fields.float('Discount 2(%)', digits=(16, 2)),
                }
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        result = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, context)
        if product_id:
            pricelist_item = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], product_id, qty or 1.0, partner_id)
            if pricelist_item[pricelist_id] is not False:
                pricelist_item_id = pricelist_item['item_id'][pricelist_id]
                price_item = self.pool.get('product.pricelist.item').browse(cr, uid, pricelist_item_id, context=context)
                result['value']['discount'] = price_item.discount_line 
                result['value']['discount2'] = price_item.discount2_line 
        return result
    
    
purchase_order_line()

class purchase_order(orm.Model):
    
    _inherit = 'purchase.order'
    
    # Amount when save/calculate purchase order
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
               val1 += line.price_subtotal
               price_net = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * (1 - (line.discount2 or 0.0) / 100.0)
               #for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']:
               for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, price_net, line.product_qty, line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    # Creating the picking
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        
        price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0) * (1 - (order_line.discount2 or 0.0) / 100.0)
        order_line.price_unit = price
        result = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=None)
        return result
    
    # Creating the invoice
   
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        result = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context=None)
        result['discount2'] = order_line.discount2 or 0.0
        return result

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    _columns = {
                'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums",help="The total amount"),
                }
    
purchase_order()

class procurement_order(orm.Model):
    
    _inherit = 'procurement.order'
    
    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from procurement
        @return: New created Purchase Orders procurement wise
        """
        res = super(procurement_order, self).make_po(cr, uid, ids, context=None)
        for procurement in self.browse(cr, uid, ids, context=context):
            # da procurement prendo id ordine x ripassare le righe e vedere il listino for
            pricelist_item = self.pool.get('product.pricelist').price_get(cr, uid, [procurement.purchase_id.pricelist_id.id], procurement.purchase_id.product_id.id, procurement.product_qty or 1.0, procurement.purchase_id.partner_id.id)
            pricelist_item_id = pricelist_item['item_id'][procurement.purchase_id.pricelist_id.id]
            price_item = self.pool.get('product.pricelist.item').browse(cr, uid, pricelist_item_id, context=context)
            
            if price_item:
                for line in procurement.purchase_id.order_line:
                    vals = {
                       'discount': price_item.discount_line,
                       'discount2': price_item.discount2_line
                       }
                    self.pool.get('purchase.order.line').write(cr, uid, [line.id], vals)
        
        return res
    
procurement_order()
    
