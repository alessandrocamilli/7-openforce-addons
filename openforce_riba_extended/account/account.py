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

from osv import fields, orm, osv
import decimal_precision as dp

# se distinta_line_ids == None allora non è stata emessa
class account_move_line(orm.Model):
    
    _inherit = "account.move.line"
    
    def _get_riba_residual_emission(self, cr, uid, ids, field_name, arg, context=None):
        commission_item_obj = self.pool.get('salesman.commission.item')
        res ={}
        for line in self.browse(cr, uid, ids, context=None):
            if line.riba_amount_residual :
                res[line.id] = line.riba_amount_residual
            else:
                res[line.id] = line.debit
            
        return res

    _columns = {
        'riba_move_unriconcile': fields.one2many('riba.move.line.unreconcile', 'move_line_id', "Riba to reconcile"),
        'riba_amount_residual': fields.float('Residuo', digits_compute=dp.get_precision('Account')),
        'riba_amount_residual_emission': fields.function(_get_riba_residual_emission, 'Residuo', digits_compute=dp.get_precision('Account')),
        #'amount': fields.function(_amount_line, string='Amount', digits_compute= dp.get_precision('Account')),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False, submenu=False):
        
        view_payments_tree_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'l10n_it_ricevute_bancarie', 'view_riba_da_emettere_tree')
        if view_id == view_payments_tree_id[1]:
            # Use RiBa list - grazie a eLBati @ account_due_list
            result = super(osv.osv, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        else:
            # Use special views for account.move.line object (for ex. tree view contains user defined fields)
            result = super(account_move_line, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        return result
    
    
class account_invoice(orm.Model):
    
    _inherit = "account.invoice"
    
    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
        """
        
        res = super(account_invoice, self).finalize_invoice_move_lines(cr, uid, invoice_browse, move_lines)
        
        return move_lines