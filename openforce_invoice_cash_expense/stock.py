# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
#    All Rights Reserved
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

import netsvc
import pooler, tools
import datetime
from openerp.osv import orm, fields

class stock_picking(orm.Model):
    
    _inherit = "stock.picking"
   
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        picking_obj = self.pool.get('stock.picking')
        invoice_line_obj = self.pool.get('account.invoice.line')
        result = super(stock_picking, self).action_invoice_create(cr, uid,
                ids, journal_id=journal_id, group=group, type=type,
                context=context)
        for picking in picking_obj.browse(cr, uid, result.keys(), context=context):
            invoice = invoice_obj.browse(cr, uid, result[picking.id], context=context)
            invoice_line = invoice_obj._prepare_cash_expense_invoice_line(cr, uid, picking, invoice, context=context)
            if invoice_line:
                invoice_line_obj.create(cr, uid, invoice_line)
                invoice_obj.button_compute(cr, uid, [invoice.id], context=context)
        return result
    
stock_picking()