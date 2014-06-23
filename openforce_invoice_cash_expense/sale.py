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
from openerp.osv import orm, fields, osv

class sale_order(orm.Model):
    
    _inherit = "sale.order"
   
    def _make_invoice(self, cr, uid, order, lines, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        
        inv_id = super(sale_order, self)._make_invoice(cr, uid, order, lines, context)
        invoice = invoice_obj.browse(cr, uid, inv_id)
        picking = None
        invoice_line = invoice_obj._prepare_cash_expense_invoice_line(cr, uid, picking, invoice, context=context)
        if invoice_line:
                invoice_line_obj.create(cr, uid, invoice_line)
                invoice_obj.button_compute(cr, uid, [invoice.id], context=context)
        return inv_id

    
class sale_advance_payment_inv(orm.Model):
    
    _inherit = "sale.advance.payment.inv"
   
    def _create_invoices(self, cr, uid, inv_values, sale_id, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        
        inv_id = super(sale_advance_payment_inv, self)._create_invoices(cr, uid, inv_values, sale_id, context)
        
        invoice = invoice_obj.browse(cr, uid, inv_id)
        picking = None
        invoice_line = invoice_obj._prepare_cash_expense_invoice_line(cr, uid, picking, invoice, context=context)
        if invoice_line:
                invoice_line_obj.create(cr, uid, invoice_line)
                invoice_obj.button_compute(cr, uid, [invoice.id], context=context)
        return inv_id
    

class sale_order_line_make_invoice(osv.osv_memory):
    _inherit = "sale.order.line.make.invoice"
    
    def make_invoices(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        
        res = super(sale_order_line_make_invoice, self).make_invoices(cr, uid, ids, context)
        
        res_id = res['res_id']
        if res_id:
            invoice = invoice_obj.browse(cr, uid, res_id)
            picking = None
            invoice_line = invoice_obj._prepare_cash_expense_invoice_line(cr, uid, picking, invoice, context=context)
            if invoice_line:
                invoice_line_obj.create(cr, uid, invoice_line)
                invoice_obj.button_compute(cr, uid, [invoice.id], context=context)
        
        return res





