# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.tools.translate import _
from osv import fields, osv, orm

class sale_order(orm.Model):
    _inherit = "sale.order"
    
    _columns = {
        'contract_required': fields.boolean('Contract required', help="If true, the contract ref is required"),
    }
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        
        # controllo esistenza project id
        for order in self.browse(cr, uid, ids):
            if order.contract_required and not order.project_id:
                raise osv.except_osv(_('Attention contract required!'),_("If not required, unflag the voice on the other information tab ") )
        
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context)

    def _make_invoice(self, cr, uid, order, lines, context={}):
        inv_id = super(sale_order, self)._make_invoice(cr, uid, order, lines, context)
        partner = self.pool.get('res.partner').browse(cr , uid, order.partner_id.id)
        self.pool.get('account.invoice').write(cr, uid, inv_id, {
#            'order_id': order.id,
            'mezzo_id': partner.mezzo_id.id,
            })
        return inv_id

    def action_ship_create(self, cr, uid, ids, *args):
        super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids, context={}):
            partner = self.pool.get('res.partner').browse(cr , uid, order.partner_id.id)
            picking_obj = self.pool.get('stock.picking.out')
            picking_ids = picking_obj.search(cr, uid, [('sale_id', '=', order.id)])
            for picking_id in picking_ids:
                picking_obj.write(cr, uid, picking_id, {
#                    'order_id': order.id,
                    'mezzo_id': partner.mezzo_id.id,
                    })
        return True
    
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(sale_order, self).default_get(cr, uid, fields, context=context)
        invoice_type_obj = self.pool.get('sale_journal.invoice.type')
        # Invoice type
        if 'invoice_type_id' not in res or not res['invoice_type_id']:
            type_ids = invoice_type_obj.search(cr, uid, [('default', '=', True)])
            if type_ids:
                res.update({'invoice_type_id':  type_ids[0]})
        
        return res
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
        invoice_type_obj = self.pool.get('sale_journal.invoice.type')
        # Invoice type
        if part:
            part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
            if part.property_invoice_type.id :
                res['value']['invoice_type_id'] = part.property_invoice_type.id
            else:
                type_ids = invoice_type_obj.search(cr, uid, [('default', '=', True)])
                if type_ids:
                    res['value']['invoice_type_id'] = type_ids[0]
                
        return res
    
class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
            #salesman_pricelist=None, user_id=None, section_id=None, discount=0, discount2=0):
        
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        
        if product:
            # Type procure method (stock/order) from product
            prod = self.pool.get('product.product').browse(cr, uid, product)
            res['value']['type'] = prod.procure_method
            
        return res