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

class account_invoice_line(orm.Model):
    
    _inherit = "account.invoice.line"
    
    _columns = {
        'cash_expense': fields.boolean('Cash Expense'),
    }
    
account_invoice_line()

class account_invoice(orm.Model):
    
    _inherit = "account.invoice"
    
    def _prepare_cash_expense_invoice_line(self, cr, uid, picking, invoice, context=None):
        """Prepare the invoice line to add to the cash expense to the shipping's
           invoice.
        """
        invoice_line_obj = self.pool.get('account.invoice.line')
        # delete expense line already exists
        expense_line_ids = invoice_line_obj.search(cr, uid, [('cash_expense','=', True),('invoice_id','=', invoice.id),], context=context)
        invoice_line_obj.unlink(cr, uid, expense_line_ids)
        
        # create a new line
        expense_amount = 0
        if invoice.payment_term.cash_expense_product_id and len(invoice.payment_term.line_ids) > 0:
            expense_amount = invoice.payment_term.cash_expense_product_id.list_price
        if expense_amount == 0:
            return False
        
        account_id = invoice.payment_term.cash_expense_product_id.property_account_income.id
        if not account_id:
            account_id = invoice.payment_term.cash_expense_product_id.categ_id\
                    .property_account_income_categ.id
        if not account_id:  
            raise osv.except_osv(_('Warning!'),
                    _('Expense cash for payment %s without account !') \
                            % (invoice.payment_term.name,))

        taxes = invoice.payment_term.cash_expense_product_id.taxes_id
        if picking:
            partner = picking.partner_id
        elif invoice:
                partner = invoice.partner_id
        else:
                partner = False
        
        # Not line if partner has exclude cash expense
        if partner and partner.cash_expense_exclude:
            return False        
        
        #partner = picking.partner_id or invoice.partner_id or False
        if partner:
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id)
            taxes_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, partner.property_account_position, taxes)
        else:
            taxes_ids = [x.id for x in taxes]

        return {
            'name': invoice.payment_term.cash_expense_product_id.name,
            'invoice_id': invoice.id,
            'uos_id': invoice.payment_term.cash_expense_product_id.uom_id.id,
            'product_id': invoice.payment_term.cash_expense_product_id.id,
            'account_id': account_id,
            'price_unit': expense_amount,
            'quantity': len(invoice.payment_term.line_ids),
            'invoice_line_tax_id': [(6, 0, taxes_ids)],
            'cash_expense': True,
        }
account_invoice()