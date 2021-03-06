# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 Alessandro Camilli
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

from osv import fields, orm
from openerp.tools.translate import _

class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        commission_order_obj = self.pool.get('salesman.commission.sale.order')
        invoice_vals = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=context)
        # Transfer commission from line order to invoice
        if move_line.sale_line_id.id :
            res = commission_order_obj.create_commission_to_invoice(cr, uid, move_line.sale_line_id.id, line_invoice_id=None, context=None)
            if res and len(res['commission_sale_invoice_ids']) > 0:
                invoice_vals['salesman_commission_ids'] = [(6, 0, res['commission_sale_invoice_ids'])]
            
        return invoice_vals
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Inherit the original function of the 'stock' module in order to override some
            values if the picking has been generated by a sales order
        """
        invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
        
        if picking.sale_id:
            invoice_vals['salesman_pricelist'] = picking.sale_id.salesman_pricelist.id
        return invoice_vals
    
stock_picking()